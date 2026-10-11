import hashlib
import json
import random
import re
import sys
import time
from pathlib import Path

import psutil

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
SEED = 20261012012
START = time.perf_counter()
SELF = psutil.Process()
PEAK = 0


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def budget():
    global PEAK
    PEAK = max(PEAK, SELF.memory_info().rss)
    assert PEAK <= 256 * 1024 * 1024
    assert time.perf_counter() - START < 180
    assert sum(path.stat().st_size for path in HERE.rglob('*') if path.is_file()) <= 16 * 1024 * 1024


def save(path, text):
    assert not path.exists(), str(path)
    path.write_text(text, encoding='utf-8', newline='\n')


def once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after, 1)


def oracle(acc, positive_m, positive_q, negative_m, negative_q):
    # 商余数定义独立于RTL的加半再移位表达式。
    multiplier, shift = (negative_m, negative_q) if acc < 0 else (positive_m, positive_q)
    quotient, remainder = divmod(abs(acc) * multiplier, 1 << shift)
    quotient += int(2 * remainder >= 1 << shift)
    return (-1 if acc < 0 else 1) * min(127, quotient)


def main():
    assert sys.version_info[:3] == (3, 12, 10) and psutil.__version__ == '7.2.2'
    paths = {
        'original': ROOT / 'report/evidence/S2B-T17/s11_source_preflight_20261012_r01/source_snapshot/src/s2b_conv_tile_engine.sv',
        'candidate': ROOT / 'tmp/2B/S2B-T17/s12_combined_prepare_20261012_r01/candidate/src/s2b_conv_tile_engine.sv',
        'descriptor': ROOT / 'report/evidence/S2B-T17/s11_source_preflight_20261012_r01/source_snapshot/src/s2a_network_descriptor_pkg.sv'}
    pins = {'original': '51b76623b29a852ebf66cb818ef947d932c14055e4acbb20bd8fe811bb32d555',
            'candidate': 'c46ed3e1e8af0089b2a78434c0b34869a2b1f5cf11071688345828f4a9c28454',
            'descriptor': 'e83a592d15908474498380bcaedb6db034a2b4e2165af6ea998335351c35f183'}
    for name, path in paths.items():
        assert path.is_file() and not path.is_symlink() and sha(path) == pins[name]
    texts = {name: path.read_bytes().decode('utf-8').replace('\r\n', '\n') for name, path in paths.items()}
    full_sources = []
    for name, module in (('original', 'rq_original_engine'), ('candidate', 'rq_candidate_engine')):
        prepared = once(texts[name], 'module s2b_conv_tile_engine', 'module ' + module)
        assert prepared.replace('module ' + module, 'module s2b_conv_tile_engine', 1) == texts[name]
        destination = HERE / (module + '.sv')
        save(destination, prepared)
        full_sources.append({'input': str(paths[name]), 'input_raw_sha256': pins[name],
                             'prepared_file': destination.name, 'prepared_sha256': sha(destination),
                             'transformation': '完整模块仅更名；UTF-8/LF；不删减逻辑、不替换生产引擎'})
    descriptor = HERE / 's2a_network_descriptor_pkg.sv'
    assert not descriptor.exists()
    descriptor.write_bytes(paths['descriptor'].read_bytes())
    beginning = texts['candidate'].index("        requant_parameter = 80'd0;")
    ending = texts['candidate'].index('        mapped_response_error = INTERNAL;', beginning)
    block = texts['candidate'][beginning:ending]
    assert 'requant_signed_value' not in block
    product = "            requant_product = {32'd0, requant_magnitude} *\n                              {32'd0, requant_multiplier};\n"
    clamp_start = block.index('            if (|requant_rounded_magnitude[63:7]) begin')
    mutations = {
        'noround': once(block, "64'd1 << (requant_q_shift - 32'd1)", "64'd0"),
        'minus128sat': once(block, "? -8'sd127 : 8'sd127", "? -8'sd128 : 8'sd127"),
        'ignorebit7': once(block, '[63:7]', '[63:8]'),
        'product32': once(block, product, product + "            requant_product = {32'd0, requant_product[31:0]};\n"),
        'signwrong': block[:clamp_start] + block[clamp_start:].replace('requant_accumulator[31]', "1'b0"),
        'shiftwrap6': once(once(block, "{24'd0, requant_parameter[7:0]}", "{26'd0, requant_parameter[5:0]}"),
                          "{24'd0, requant_parameter[47:40]}", "{26'd0, requant_parameter[45:40]}"),
        'negativeusespositive': once(once(block, 'requant_multiplier = requant_parameter[39:8];', 'requant_multiplier = requant_parameter[79:48];'),
                                     "requant_q_shift = {24'd0, requant_parameter[7:0]};", "requant_q_shift = {24'd0, requant_parameter[47:40]};")}
    mutant_text = []
    for name, body in mutations.items():
        assert body != block
        mutant_text.append('''// 仅提取requant组合块的语义变异；不是全核心变异。
module rq_mutant_''' + name + ''' (
    input logic signed [31:0] accumulator,
    input logic [79:0] parameter_word,
    output logic signed [7:0] requantized_value
);
    localparam integer LANE_COUNT = 8;
    logic [31:0] requant_lane_index, group_lane_count;
    logic [79:0] lane_mq_parameter [0:7];
    logic signed [31:0] lane_accumulator [0:7];
    logic [79:0] requant_parameter;
    logic signed [31:0] requant_accumulator;
    logic [31:0] requant_multiplier, requant_q_shift, requant_magnitude;
    logic [63:0] requant_product, requant_rounding_add, requant_rounded_magnitude;
    always_comb begin
        requant_lane_index = 0;
        group_lane_count = 1;
        for (integer lane = 0; lane < 8; lane = lane + 1) begin
            lane_mq_parameter[lane] = 0;
            lane_accumulator[lane] = 0;
        end
        lane_mq_parameter[0] = parameter_word;
        lane_accumulator[0] = accumulator;
''' + body + '''    end
endmodule
''')
    save(HERE / 'requant_mutants.sv', '\n'.join(mutant_text))
    declarations = re.findall(r'^\s*(input|output)\s+logic\s+(?:signed\s+)?(?:\[[^\]]+\]\s+)?(\w+)\s*[,)]?',
                              texts['original'].split(');', 1)[0], re.M)
    assert len(declarations) == 51, len(declarations)
    candidate_declarations = re.findall(r'^\s*(input|output)\s+logic\s+(?:signed\s+)?(?:\[[^\]]+\]\s+)?(\w+)\s*[,)]?',
                                       texts['candidate'].split(');', 1)[0], re.M)
    assert declarations == candidate_declarations
    connections = ',\n'.join('        .' + name + "('0)" if direction == 'input' else '        .' + name + '()'
                               for direction, name in declarations)
    instances = '    rq_original_engine original_engine (\n' + connections + '\n    );\n'
    instances += "    rq_candidate_engine #(.FROZEN_CONV_DESCRIPTOR(1'b0)) candidate_engine (\n" + connections + '\n    );\n'
    instances += '\n'.join(f'    rq_mutant_{name} mutant_{index} (.accumulator(accumulator), .parameter_word(parameter_word), .requantized_value(mutant_value[{index}]));'
                           for index, name in enumerate(mutations))
    tb = '''// 完整原模块及完整合并候选的白盒二态组合核验；不是公开FSM输入可达性测试。
module tb_s12_requant;
    logic signed [31:0] accumulator;
    logic [79:0] parameter_word;
    logic signed [7:0] expected_file, expected_oracle;
    wire signed [7:0] mutant_value [0:6];
    integer mutant_hits [0:6];
    integer fd, fields, case_id, vectors, mismatch_count;
''' + instances + '''
    function automatic logic signed [7:0] division_oracle(
        input logic signed [31:0] value,
        input logic [79:0] mq
    );
        logic [31:0] multiplier;
        logic [7:0] shift;
        logic [63:0] magnitude;
        logic [255:0] numerator, denominator, quotient, remainder;
        begin
            multiplier = value[31] ? mq[39:8] : mq[79:48];
            shift = value[31] ? mq[7:0] : mq[47:40];
            magnitude = value[31] ? -$signed({{32{value[31]}}, value}) : {32'd0, value};
            numerator = magnitude * {32'd0, multiplier};
            denominator = 256'd1 << shift;
            quotient = numerator / denominator;
            remainder = numerator % denominator;
            if ((remainder << 1) >= denominator) quotient = quotient + 256'd1;
            if (quotient > 256'd127) division_oracle = value[31] ? -8'sd127 : 8'sd127;
            else division_oracle = value[31] ? -$signed(quotient[7:0]) : $signed(quotient[7:0]);
        end
    endfunction

    initial begin
        vectors = 0;
        mismatch_count = 0;
        for (integer index = 0; index < 7; index = index + 1) mutant_hits[index] = 0;
        // clk固定为0；直接装载内部寄存器，不通过公开接口绕过或更改参数校验。
        original_engine.requant_lane_index = 0;
        candidate_engine.requant_lane_index = 0;
        original_engine.group_lane_count = 1;
        candidate_engine.group_lane_count = 1;
        fd = $fopen("vectors.txt", "r");
        if (!fd) $fatal(1, "VECTORS_OPEN_FAILED");
        while (!$feof(fd)) begin
            fields = $fscanf(fd, "%h %h %h %d\\n", accumulator, parameter_word, expected_file, case_id);
            if (fields == 4) begin
                original_engine.lane_accumulator[0] = accumulator;
                candidate_engine.lane_accumulator[0] = accumulator;
                original_engine.lane_mq_parameter[0] = parameter_word;
                candidate_engine.lane_mq_parameter[0] = parameter_word;
                #1;
                expected_oracle = division_oracle(accumulator, parameter_word);
                if ((expected_oracle !== expected_file) ||
                    (original_engine.requantized_value !== expected_oracle) ||
                    (candidate_engine.requantized_value !== expected_oracle)) begin
                    mismatch_count = mismatch_count + 1;
                    if (mismatch_count <= 12)
                        $display("REQUANT_MISMATCH case=%0d acc=%h mq=%h old=%h new=%h oracle=%h file=%h", case_id,
                                 accumulator, parameter_word, original_engine.requantized_value,
                                 candidate_engine.requantized_value, expected_oracle, expected_file);
                end
                for (integer index = 0; index < 7; index = index + 1) begin
                    if (mutant_value[index] !== expected_oracle) begin
                        mutant_hits[index] = mutant_hits[index] + 1;
                        if (mutant_hits[index] == 1)
                            $display("MUTANT_SEMANTIC_WITNESS id=%0d case=%0d acc=%h mq=%h actual=%h oracle=%h", index,
                                     case_id, accumulator, parameter_word, mutant_value[index], expected_oracle);
                    end
                end
                vectors = vectors + 1;
            end else if (fields != -1) $fatal(1, "MALFORMED_VECTOR fields=%0d", fields);
        end
        $fclose(fd);
        if (mismatch_count != 0) $fatal(1, "FULL_RTL_ORACLE_MISMATCH count=%0d", mismatch_count);
        for (integer index = 0; index < 7; index = index + 1) begin
            if (mutant_hits[index] == 0) $fatal(1, "MUTANT_SURVIVED id=%0d", index);
            $display("MUTANT_SEMANTIC_KILLED id=%0d count=%0d", index, mutant_hits[index]);
        end
        $display("S12_REQUANT_FULL_RTL_PASS vectors=%0d mutants=7 mismatches=0", vectors);
        $finish;
    end
endmodule
'''
    save(HERE / 'tb_s12_requant.sv', tb)
    rng = random.Random(SEED)
    count = legal = 0
    witnesses = [(1, 1, 1, 2, 0), (-128, 3, 1, 1, 0), (128, 1, 0, 7, 2),
                 (65536, 65536, 0, 9, 0), (-1, 3, 0, 1, 0),
                 (-(1 << 31), 1, 0, 0xFFFFFFFF, 64), (-2, 1, 0, 2, 0)]
    vector_path = HERE / 'vectors.txt'
    assert not vector_path.exists()
    with vector_path.open('w', encoding='utf-8', newline='\n') as stream:
        def emit(a, pm, pq, nm, nq):
            nonlocal count, legal
            expected = oracle(a, pm, pq, nm, nq)
            parameter = (pm << 48) | (pq << 40) | (nm << 8) | nq
            stream.write(f'{a & 0xFFFFFFFF:08x} {parameter:020x} {expected & 0xFF:02x} {count}\n')
            count += 1
            legal += int(1 <= pm <= 0x3FFFFFFF and 1 <= nm <= 0x3FFFFFFF and pq <= 47 and nq <= 47)
            if count % 4096 == 0:
                budget()
        for row in witnesses:
            emit(*row)
        accumulators = [-2**31, -2**31 + 1, -2**30, -65536, -257, -256, -255, -129, -128, -127, -126,
                        -3, -2, -1, 0, 1, 2, 3, 126, 127, 128, 129, 255, 256, 257, 65536, 2**30, 2**31 - 2, 2**31 - 1]
        multipliers = [0, 1, 2, 3, 127, 128, 255, 256, 65535, 65536, 2**30 - 1, 2**30, 2**31 - 1,
                       2**31, 2**32 - 2, 2**32 - 1]
        for a in accumulators:
            for m in multipliers:
                for q in range(256):
                    other_m = (m ^ 0x13579BDF) & 0xFFFFFFFF
                    other_q = (q + 17) & 0xFF
                    emit(a, other_m if a < 0 else m, other_q if a < 0 else q,
                         m if a < 0 else other_m, q if a < 0 else other_q)
        for _ in range(10000):
            emit(rng.randrange(-2**31, 2**31), rng.randrange(1, 2**30), rng.randrange(48), rng.randrange(1, 2**30), rng.randrange(48))
        for _ in range(10000):
            emit(rng.randrange(-2**31, 2**31), rng.randrange(2**32), rng.randrange(256), rng.randrange(2**32), rng.randrange(256))
    budget()
    files = [{'path': path.name, 'sha256': sha(path), 'bytes': path.stat().st_size}
             for path in sorted(HERE.iterdir()) if path.is_file() and path.name not in ('prepare.stdout.log', 'prepare.stderr.log')]
    result = {'status': 'PREPARED_NOT_COMPILED', 'source_evidence_head': '891f750045ce141a8152c96025da559ff1d3a321',
              'sources': full_sources, 'descriptor_raw_sha256': pins['descriptor'],
              'mutant_exact_block_sha256': hashlib.sha256(block.encode('utf-8')).hexdigest(),
              'mutants': list(mutations), 'vectors': count, 'both_branch_parameters_legal_vectors': legal,
              'seed': SEED, 'random_vectors': 20000, 'witness_vectors_first7': witnesses,
              'prepared_files': files, 'python': sys.version, 'psutil': psutil.__version__,
              'elapsed_seconds': time.perf_counter() - START, 'sampled_self_rss_peak_bytes': PEAK,
              'absolute_process_tree_peak_bytes': None,
              'compile_status': 'NOT_RUN_ROOT_HEAVY_SLOT_REQUIRED', 'simulation_status': 'NOT_RUN',
              'limits': {'prepare_bytes': 16 * 1024 * 1024, 'prepare_tree_bytes': 256 * 1024 * 1024, 'prepare_seconds': 180,
                         'execute_bytes': 640 * 1024 * 1024, 'execute_tree_bytes': 1024 * 1024 * 1024, 'execute_seconds': 600},
              'limitations': ['二态白盒内部寄存器装载；非法M/q样例不声称公共FSM可达',
                              '完整原模块与完整合并候选源绑定构建，候选仅FROZEN_CONV_DESCRIPTOR=0',
                              '7个mutants仅提取requant组合块，语义击杀尚NOT_RUN；SHA不同不是击杀',
                              'X/Z未测；公共全trace、ARG/overflow/abort/reset由Pool整体回归',
                              '本准备没有RTL编译、仿真、STA、独审或实板结论']}
    save(HERE / 'prepare_manifest.json', json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('status', 'vectors', 'both_branch_parameters_legal_vectors', 'elapsed_seconds', 'sampled_self_rss_peak_bytes')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
