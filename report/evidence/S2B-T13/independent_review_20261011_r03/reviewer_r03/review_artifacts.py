#!/usr/bin/env python3
"""独立只读核验真实BD、XSA、属性读回与原生capture，不执行工程命令。"""
import hashlib
import json
import subprocess
import tkinter
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

root=Path(__file__).absolute().parents[4]
out=Path(__file__).absolute().parent
run_dir=root/'report/evidence/S2B-T13/ipi_full_20261011_r05'
interp=tkinter.Tcl()
def dictionary(text):
    """只解析Tcl数据列表，不执行Tcl脚本。"""
    items=interp.splitlist(text)
    assert len(items)%2==0
    return dict(zip(items[::2],items[1::2]))
def receipt(name):
    return dictionary(dictionary((run_dir/(name+'.tcldict')).read_text(encoding='utf-8'))['data'])
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

static=json.loads((out/'static_result.json').read_text(encoding='utf-8'))
for path,value in static['source_sha256'].items(): assert digest(root/path)==value,path
capture={}
for name in ['ps7_configure','axi_gp0_lite_configure','rst_fclk0_configure','const_zero_configure','const_one_configure','connect','validate','audit','products']:
    item=receipt(name)
    capture[name]={key:item.get(key) for key in ['status','code','raw','warning_count','critical_count','error_count','unprinted_warning_count','capture_error']}
    assert item['code']=='0' and item['critical_count']=='0' and item['error_count']=='0',name
    if name!='products': assert item['status']=='OK',name
    else:
        assert item['status']=='FAIL' and item['raw']=='PRODUCTS:OK'
        assert item['capture_error']=='CAPTURE_FAIL:native message export incomplete or counters changed: WARNING emitted=-8 exported=2'

readback=receipt('platform_readback')
assert readback['part']=='xc7z020clg400-2' and readback['visibility_parameter']=='0'
interface=dictionary(readback['interfaces'])
for name,protocol,data,id_width in [('/ps7/M_AXI_GP0','AXI3',32,12),('/axi_gp0_lite/S_AXI','AXI3',32,12),
 ('/axi_gp0_lite/M_AXI','AXI4LITE',32,0),('/infer/S_AXI','AXI4LITE',32,0),('/infer/M_AXI','AXI3',64,6),('/ps7/S_AXI_HP0','AXI3',64,6)]:
    values=dictionary(interface[name])
    assert values['CONFIG.PROTOCOL']==protocol and int(values['CONFIG.DATA_WIDTH'])==data
    assert int(values['CONFIG.ADDR_WIDTH'])==32 and int(values['CONFIG.ID_WIDTH'])==id_width
scalar=dictionary(readback['scalar_pins'])
assert dictionary(scalar['infer/clk'])['CONFIG.ASSOCIATED_BUSIF']=='S_AXI:M_AXI'
assert dictionary(scalar['infer/cold_resetn'])['CONFIG.POLARITY']=='ACTIVE_LOW'
physical=dictionary(readback['physical_ports'])
assert set(interp.splitlist(physical['interfaces']))=={'DDR','FIXED_IO'}
members=dictionary(physical['members'])
assert set(interp.splitlist(physical['scalar_ports']))==set(interp.splitlist(members['DDR'])+interp.splitlist(members['FIXED_IO']))
assert len(interp.splitlist(physical['scalar_ports']))==21

bd_path=run_dir/'s2b_inference.bd'
design=json.loads(bd_path.read_text(encoding='utf-8'))['design']
assert design['design_info']['validated']=='true'
assert set(design['components'])=={'ps7','axi_gp0_lite','rst_fclk0','const_zero','const_one','infer'}
assert set(design['interface_ports'])=={'DDR','FIXED_IO'}
assert design['components']['infer']['reference_info']['ref_name']=='s2b_inference_top'
assert design['components']['infer']['parameters']['PROFILE_VISIBILITY_PROVEN']['value']=='0'
assert set(design['interface_nets']['infer_M_AXI']['interface_ports'])=={'infer/M_AXI','ps7/S_AXI_HP0'}
assert set(design['interface_nets']['ps7_M_AXI_GP0']['interface_ports'])=={'ps7/M_AXI_GP0','axi_gp0_lite/S_AXI'}
assert set(design['interface_nets']['axi_gp0_lite_M_AXI']['interface_ports'])=={'axi_gp0_lite/M_AXI','infer/S_AXI'}
assert set(design['nets']['ps7_FCLK_CLK0']['ports'])=={'ps7/FCLK_CLK0','ps7/M_AXI_GP0_ACLK','ps7/S_AXI_HP0_ACLK','axi_gp0_lite/aclk','rst_fclk0/slowest_sync_clk','infer/clk'}
assert set(design['nets']['ps7_FCLK_RESET0_N']['ports'])=={'ps7/FCLK_RESET0_N','rst_fclk0/ext_reset_in'}
assert set(design['nets']['rst_fclk0_peripheral_aresetn']['ports'])=={'rst_fclk0/peripheral_aresetn','axi_gp0_lite/aresetn','infer/cold_resetn'}
assert set(design['nets']['const_zero_dout']['ports'])=={'const_zero/dout','rst_fclk0/aux_reset_in','rst_fclk0/mb_debug_sys_rst'}
assert set(design['nets']['const_one_dout']['ports'])=={'const_one/dout','rst_fclk0/dcm_locked'}
ctrl=design['addressing']['/ps7']['address_spaces']['Data']['segments']
assert ctrl=={'SEG_infer_reg0':{'address_block':'/infer/S_AXI/reg0','offset':'0x43C00000','range':'64K'}}
hp=design['addressing']['/infer']['address_spaces']['M_AXI']['segments']
assert hp=={'SEG_ps7_HP0_DDR_LOWOCM':{'address_block':'/ps7/S_AXI_HP0/HP0_DDR_LOWOCM','offset':'0x00000000','range':'1G'}}

ps=receipt('ps7_readback')
requested,actual=dictionary(ps['requested']),dictionary(ps['actual'])
# 只读取已审PS profile声明函数，保留同六字段增量后的真实请求全集。
ps_query=('source {'+str(root/'vivado/s2b_ps_platform.tcl').replace('\\','/')+'}\nputs [::s2b_ps_platform::requested]\n').encode('utf-8')
process=subprocess.run(['C:/Program Files/Git/ucrt64/bin/tclsh.exe'],input=ps_query,capture_output=True)
assert process.returncode==0
(out/'ps_requested.stdout.log').write_bytes(process.stdout)
expected=dictionary(process.stdout.decode('utf-8').strip())
expected.update({'CONFIG.PCW_USE_M_AXI_GP0':'1','CONFIG.PCW_USE_S_AXI_HP0':'1','CONFIG.PCW_S_AXI_HP0_DATA_WIDTH':'64',
 'CONFIG.PCW_EN_CLK0_PORT':'1','CONFIG.PCW_EN_RST0_PORT':'1','CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ':'50'})
assert requested==expected
assert actual==expected
bd_ps_parameters=design['components']['ps7']['parameters']
bd_default_omissions=[]
for key,value in expected.items():
    name=key.removeprefix('CONFIG.')
    if name in bd_ps_parameters:
        assert bd_ps_parameters[name]['value']==value,key
    else:
        bd_default_omissions.append(key)

xsa_path=run_dir/'s2b_inference_no_bit.xsa'
with zipfile.ZipFile(xsa_path) as z:
    assert z.testzip() is None
    assert not any(name.lower().endswith('.bit') for name in z.namelist())
    metadata=json.loads(z.read('xsa.json'))
    assert metadata['platformState']=='pre_synth' and metadata['topModuleName']=='s2b_inference_wrapper'
    assert metadata['devices'][0]['part']['name']=='xc7z020clg400-2'
    hwh=ET.fromstring(z.read('s2b_inference.hwh'))
    ps_module=hwh.find('.//MODULE[@INSTANCE="ps7"]')
    ps_parameters={p.attrib['NAME']:p.attrib['VALUE'] for p in ps_module.findall('./PARAMETERS/PARAMETER')}
    for key,value in expected.items():
        assert ps_parameters[key.removeprefix('CONFIG.')]==value,key
    module=hwh.find('.//MODULE[@INSTANCE="infer"]')
    params={p.attrib['NAME']:p.attrib['VALUE'] for p in module.findall('./PARAMETERS/PARAMETER')}
    assert params['PROFILE_VISIBILITY_PROVEN']=='0' and params['C_BASEADDR']=='0x43C00000' and params['C_HIGHADDR']=='0x43C0FFFF'
    widths={'m_axi_awaddr':32,'m_axi_araddr':32,'m_axi_awid':6,'m_axi_arid':6,'m_axi_wid':6,'m_axi_bid':6,'m_axi_rid':6,
      'm_axi_awlen':4,'m_axi_arlen':4,'m_axi_awlock':2,'m_axi_arlock':2,'m_axi_wdata':64,'m_axi_rdata':64,'m_axi_wstrb':8,
      'm_axi_awcache':4,'m_axi_arcache':4,'s_axi_awaddr':32,'s_axi_araddr':32,'s_axi_wdata':32,'s_axi_rdata':32}
    ports={p.attrib['NAME']:p for p in module.findall('./PORTS/PORT')}
    for name,width in widths.items():
        port=ports[name]
        assert int(port.attrib.get('LEFT','0'))-int(port.attrib.get('RIGHT','0'))+1==width,name
        connections=port.findall('./CONNECTIONS/CONNECTION')
        assert len(connections)==1
        if name.startswith('m_axi_'):
            assert connections[0].attrib=={'INSTANCE':'ps7','PORT':'S_AXI_HP0_'+name.removeprefix('m_axi_').upper()},name
        else:
            assert connections[0].attrib['INSTANCE']=='axi_gp0_lite',name
    xsa_files={name:hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist()}
assert all(digest(root/path)==value for path,value in static['source_sha256'].items())
result={'status':'ACTUAL_ARTIFACTS_PASS_PENDING_PACKAGING_RECOVERY','source_sha256':static['source_sha256'],
 'capture':capture,'readback_source_sha256':digest(run_dir/'platform_readback.tcldict'),'physical_scalar_ports':21,
 'ps_profile_fields_verified':len(expected),'bd_default_omissions_checked_against_actual_and_hwh':bd_default_omissions,
 'bd_sha256':digest(bd_path),'xsa_sha256':digest(xsa_path),'xsa_member_sha256':xsa_files,
 'checks':['真实validate/audit0，原产品命令0但captureFAIL原样保留','完整GP0转换/HP0直连/AXI3 widths及真实HWH逐信号连接',
 '50MHz同域/复位全部网/DDR与FIXED_IO唯一外接口、21成员','PS厂商声明全部字段+六PL增量匹配request/actual/BD',
 'BD物理地址64KiB、HP1GiB；guard32MiB逐对象仍由源码限定','ZIP CRC完整、pre_synth/no_bit/XSA参数0与BD一致'],
 'limits':['未实际综合、实现、位流、时序或实板。','只候选平台0，不批准visibility1。','原captureWARN history失败需root冻结可复核产物恢复入口。',
 '最终同ELF XSA0↔XSA1兼容证明待独立实际核验；不能假装已关闭。']}
(out/'actual_artifact_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('R3_ACTUAL_ARTIFACTS:PASS_PENDING_PACKAGING_RECOVERY')
