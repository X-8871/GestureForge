#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
repo_root_win="$(cygpath -aw "$repo_root")"
vendor_root="$repo_root/tmp/stage3_reference/AX7020_2023.1"
vendor_root_win="$(cygpath -aw "$vendor_root")"
authorized_root="$repo_root/tmp/s3r04"
authorized_root_win="$(cygpath -aw "$authorized_root")"
config_path="$repo_root/scripts/stage3_t03/NuGet.Config"
config_path_win="$(cygpath -aw "$config_path")"

if [[ "$(uname -s)" != MINGW* && "$(uname -s)" != MSYS* ]]; then
    printf '%s\n' 'PATH_GUARD_SELFTEST=FAIL;REASON=GIT_BASH_REQUIRED' >&2
    exit 2
fi
if [[ ! -d "$vendor_root" || -L "$vendor_root" || ! -d "$authorized_root" || -L "$authorized_root" ]]; then
    printf '%s\n' 'PATH_GUARD_SELFTEST=FAIL;REASON=ROOT_OR_VENDOR_DIRECTORY_INVALID' >&2
    exit 2
fi
if [[ "$(git -C "$vendor_root" rev-parse HEAD)" != fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327 ]]; then
    printf '%s\n' 'PATH_GUARD_SELFTEST=FAIL;REASON=VENDOR_COMMIT_MISMATCH' >&2
    exit 2
fi
if [[ -n "$(git -C "$vendor_root" status --porcelain=v1 --untracked-files=all --ignored=matching -- course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project)" ]]; then
    printf '%s\n' 'PATH_GUARD_SELFTEST=FAIL;REASON=VENDOR_SOURCE_NOT_CLEAN' >&2
    exit 2
fi

tag="$(date -u +%Y%m%dT%H%M%S)_${RANDOM}_${RANDOM}"
prefix="stage1_pathguard_${tag}"
build_dir="$authorized_root/${prefix}_build"
build_dir_win="$(cygpath -aw "$build_dir")"
expected_file_count="$(git -C "$vendor_root" ls-files -- course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project/my_ip | wc -l | tr -d '[:space:]')"
if [[ -e "$build_dir" || -L "$build_dir" ]]; then
    printf '%s\n' 'PATH_GUARD_SELFTEST=FAIL;REASON=BUILD_DIRECTORY_COLLISION' >&2
    exit 2
fi
mkdir "$build_dir"

export DOTNET_CLI_HOME="$build_dir_win/dotnet-home"
export APPDATA="$build_dir_win/appdata"
export NUGET_PACKAGES="$build_dir_win/nuget"
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
export DOTNET_CLI_TELEMETRY_OPTOUT=1

obj_dir_win="$build_dir_win/obj/"
bin_dir_win="$build_dir_win/bin/"
nuget_dir_win="$build_dir_win/nuget"
dotnet restore "$repo_root/scripts/stage3_t03/Stage3T03.Helper.csproj" \
    --configfile "$config_path_win" \
    -p:RestoreConfigFile="$config_path_win" \
    -p:BaseIntermediateOutputPath="$obj_dir_win" \
    -p:RestorePackagesPath="$nuget_dir_win" \
    -p:NuGetAudit=false --ignore-failed-sources
dotnet build "$repo_root/scripts/stage3_t03/Stage3T03.Helper.csproj" --no-restore \
    -p:BaseIntermediateOutputPath="$obj_dir_win" \
    -p:BaseOutputPath="$bin_dir_win" \
    -p:RestorePackagesPath="$nuget_dir_win" \
    -p:NuGetAudit=false

helper_dll="$build_dir/bin/Debug/net10.0-windows/Stage3T03.Helper.dll"
helper_dll_win="$(cygpath -aw "$helper_dll")"
passed=0
bd_tree_sha=""
hdl_tree_sha=""

compute_tree_sha() {
    local tree_root="$1"
    local canonical="FILE_COUNT=0"$'\n'
    local file relative digest
    local -a files=()
    mapfile -d '' -t files < <(find "$tree_root" -type f -print0 | LC_ALL=C sort -z)
    canonical="FILE_COUNT=${#files[@]}"$'\n'
    for file in "${files[@]}"; do
        relative="${file#"$tree_root"/}"
        digest="$(sha256sum -- "$file" | cut -d' ' -f1 | tr '[:lower:]' '[:upper:]')"
        canonical+="$digest  $relative"$'\n'
    done
    printf '%s' "$canonical" | sha256sum | cut -d' ' -f1 | tr '[:lower:]' '[:upper:]'
}

run_pass_case() {
    local phase="$1"
    local mode="$2"
    local suffix="$3"
    local expected="$4"
    local output_dir="$authorized_root/${prefix}_${suffix}"
    local output_dir_win
    local result
    output_dir_win="$(cygpath -aw "$output_dir")"
    if [[ -e "$output_dir" || -L "$output_dir" ]]; then
        printf 'PATH_GUARD_SELFTEST=FAIL;REASON=OUTPUT_COLLISION;CASE=%s\n' "$suffix" >&2
        exit 2
    fi
    result="$(dotnet "$helper_dll_win" path-guard --repo-root "$repo_root_win" --vendor-root "$vendor_root_win" \
        --output-dir "$output_dir_win" --mode "$mode" --phase "$phase")"
    if [[ "$result" != *"$expected"* ]]; then
        printf 'PATH_GUARD_SELFTEST=FAIL;REASON=RESULT_MISMATCH;CASE=%s\n%s\n' "$suffix" "$result" >&2
        exit 2
    fi
    if [[ "$mode" == azynq_metadata ]]; then
        local count_line tree_line tree_sha computed_sha
        count_line="$(printf '%s\n' "$result" | rg '^METADATA_COPY_FILE_COUNT=')"
        tree_line="$(printf '%s\n' "$result" | rg '^METADATA_TREE_SHA256=')"
        tree_sha="${tree_line#METADATA_TREE_SHA256=}"
        computed_sha="$(compute_tree_sha "$output_dir/vendor_ip_metadata")"
        if [[ "$count_line" != "METADATA_COPY_FILE_COUNT=$expected_file_count" || ! "$tree_sha" =~ ^[A-F0-9]{64}$ || "$tree_sha" != "$computed_sha" ]]; then
            printf 'PATH_GUARD_SELFTEST=FAIL;REASON=METADATA_DIGEST_OR_COUNT_INVALID;CASE=%s\n' "$suffix" >&2
            exit 2
        fi
        if [[ "$suffix" == bdmeta ]]; then bd_tree_sha="$tree_sha"; fi
        if [[ "$suffix" == hdlmeta ]]; then hdl_tree_sha="$tree_sha"; fi
        local secure_file secure_file_win payload_one payload_two encoded_one encoded_two write_result read_result hash_result tree_result tree_digest outside_result outside_exit source_root_win validator_win secure_digest
        secure_file="$output_dir/project/secure_io_probe.txt"
        secure_file_win="$(cygpath -aw "$secure_file")"
        payload_one='secure-io stage3 probe one'
        payload_two='secure-io stage3 probe two'
        encoded_one="$(printf '%s' "$payload_one" | base64 -w0)"
        encoded_two="$(printf '%s' "$payload_two" | base64 -w0)"
        write_result="$(printf '%s' "$encoded_one" | dotnet "$helper_dll_win" secure-io write "$output_dir_win" "$secure_file_win" CreateNew)"
        if [[ "$write_result" != 'S3_SECURE_WRITE=PASS' ]]; then
            printf 'PATH_GUARD_SELFTEST=FAIL;REASON=SECURE_IO_CREATE_FAILED;CASE=%s\n%s\n' "$suffix" "$write_result" >&2
            exit 2
        fi
        secure_digest="$(printf '%s' "$payload_one" | sha256sum | cut -d' ' -f1 | tr '[:lower:]' '[:upper:]')"
        read_result="$(dotnet "$helper_dll_win" secure-io read "$output_dir_win" "$secure_file_win")"
        if [[ "$read_result" != "S3_SECURE_READ=$secure_digest:$encoded_one" ]]; then
            printf 'PATH_GUARD_SELFTEST=FAIL;REASON=SECURE_IO_READ_MISMATCH;CASE=%s\n%s\n' "$suffix" "$read_result" >&2
            exit 2
        fi
        secure_digest="$(printf '%s' "$payload_two" | sha256sum | cut -d' ' -f1 | tr '[:lower:]' '[:upper:]')"
        write_result="$(printf '%s' "$encoded_two" | dotnet "$helper_dll_win" secure-io write-hash "$output_dir_win" "$secure_file_win" OpenExisting)"
        if [[ "$write_result" != "S3_SECURE_WRITE=PASS:$secure_digest" ]]; then
            printf 'PATH_GUARD_SELFTEST=FAIL;REASON=SECURE_IO_HASH_WRITE_MISMATCH;CASE=%s\n%s\n' "$suffix" "$write_result" >&2
            exit 2
        fi
        source_root_win="$(cygpath -aw "$vendor_root/course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project")"
        validator_win="$(cygpath -aw "$repo_root/scripts/s3_validate_hdmi_only_bd.tcl")"
        hash_result="$(dotnet "$helper_dll_win" secure-io hash-files "$output_dir_win" \
            "$source_root_win/ps_config.tcl" "$validator_win")"
        if [[ "$(printf '%s\n' "$hash_result" | wc -l | tr -d '[:space:]')" != 2 ||
              "$(printf '%s\n' "$hash_result" | rg -c '^[A-F0-9]{64}\t')" != 2 ]]; then
            printf 'PATH_GUARD_SELFTEST=FAIL;REASON=SECURE_IO_HASH_FILES_INVALID;CASE=%s\n%s\n' "$suffix" "$hash_result" >&2
            exit 2
        fi
        tree_result="$(dotnet "$helper_dll_win" secure-io tree-hash "$output_dir_win" "$(cygpath -aw "$output_dir/vendor_ip_metadata")")"
        tree_digest="$(printf '%s\n' "$tree_result" | rg '^S3_SECURE_TREE_ROOT_SHA256=' | cut -d= -f2)"
        if [[ "$(printf '%s\n' "$tree_result" | wc -l | tr -d '[:space:]')" != "$((expected_file_count + 1))" ||
              "$(printf '%s\n' "$tree_result" | rg -c '^S3_SECURE_TREE_SHA256=[A-F0-9]{64}\t')" != "$expected_file_count" ]]; then
            printf 'PATH_GUARD_SELFTEST=FAIL;REASON=SECURE_IO_TREE_HASH_INVALID;CASE=%s\n%s\n' "$suffix" "$tree_result" >&2
            exit 2
        fi
        if [[ "$tree_digest" != "$computed_sha" ]]; then
            printf 'PATH_GUARD_SELFTEST=FAIL;REASON=SECURE_IO_TREE_ROOT_DIGEST_MISMATCH;CASE=%s;EXPECTED=%s;ACTUAL=%s\n' "$suffix" "$computed_sha" "$tree_digest" >&2
            exit 2
        fi
        outside_exit=0
        outside_result="$(dotnet "$helper_dll_win" secure-io write "$output_dir_win" "$vendor_root_win/course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project/pl_config.tcl" CreateNew 2>&1)" || outside_exit=$?
        if [[ "$outside_exit" -ne 3 || "$outside_result" != *SECURE_IO_TARGET_OUTSIDE_RUN_ROOT* ]]; then
            printf 'PATH_GUARD_SELFTEST=FAIL;REASON=SECURE_IO_OUTSIDE_ROOT_ACCEPTED;CASE=%s;EXIT=%s\n%s\n' "$suffix" "$outside_exit" "$outside_result" >&2
            exit 2
        fi
        printf 'CASE=%s;RESULT=PASS;METADATA_FILES=%s;TREE_SHA256=%s\n' "$suffix" "$expected_file_count" "$tree_sha"
    else
        printf 'CASE=%s;RESULT=PASS;EXPECTED=%s\n' "$suffix" "$expected"
    fi
    passed=$((passed + 1))
}

run_fail_case() {
    local suffix="$1"
    local output_dir_win="$2"
    local expected="$3"
    local phase="${4:-guard}"
    local mode="${5:-native}"
    local result
    local exit_code=0
    result="$(dotnet "$helper_dll_win" path-guard --repo-root "$repo_root_win" --vendor-root "$vendor_root_win" \
        --output-dir "$output_dir_win" --mode "$mode" --phase "$phase" 2>&1)" || exit_code=$?
    if [[ "$exit_code" -eq 0 || "$result" != *"$expected"* ]]; then
        printf 'PATH_GUARD_SELFTEST=FAIL;REASON=REJECTION_NOT_PROVEN;CASE=%s;EXIT=%s\n%s\n' "$suffix" "$exit_code" "$result" >&2
        exit 2
    fi
    printf 'CASE=%s;RESULT=REJECTED_AS_EXPECTED;EXIT=%s;MESSAGE=%s\n' "$suffix" "$exit_code" "$result"
    passed=$((passed + 1))
}

run_fail_internal_case() {
    local suffix="$1"
    local expected="$2"
    shift 2
    local result exit_code=0
    result="$(dotnet "$helper_dll_win" "$@" 2>&1)" || exit_code=$?
    if [[ "$exit_code" -eq 0 || "$result" != *"$expected"* ]]; then
        printf 'PATH_GUARD_SELFTEST=FAIL;REASON=INTERNAL_REJECTION_NOT_PROVEN;CASE=%s;EXIT=%s\n%s\n' "$suffix" "$exit_code" "$result" >&2
        exit 2
    fi
    printf 'CASE=%s;RESULT=REJECTED_AS_EXPECTED;EXIT=%s;MESSAGE=%s\n' "$suffix" "$exit_code" "$result"
    passed=$((passed + 1))
}

run_pass_case guard native guard PASS_PATH_PREFLIGHT
if [[ -e "$authorized_root/${prefix}_guard" || -L "$authorized_root/${prefix}_guard" ]]; then
    printf '%s\n' 'PATH_GUARD_SELFTEST=FAIL;REASON=GUARD_PREFLIGHT_CREATED_OUTPUT' >&2
    exit 2
fi
run_pass_case race_test native race PASS_ATOMIC_CONCURRENT_OUTPUT_CREATE
run_pass_case lock_test native lock DELETE_ACCESS_NO_DELETE_SHARE_RENAME_TEST=PASS
run_pass_case source_lock_test native source_lock SOURCE_WRITE_ACCESS_DENIED_WHILE_PINNED=PASS
run_pass_case subpath_reparse_test native reparse PASS_PARENT_AND_SUBPATH_REPARSE_REJECTED
run_pass_case bd azynq_metadata bdmeta METADATA_WRITE_LOCK=PASS
run_pass_case hdl azynq_metadata hdlmeta METADATA_WRITE_LOCK=PASS
if [[ -z "$bd_tree_sha" || "$bd_tree_sha" != "$hdl_tree_sha" ]]; then
    printf '%s\n' 'PATH_GUARD_SELFTEST=FAIL;REASON=BD_HDL_TREE_HASH_MISMATCH' >&2
    exit 2
fi
printf 'BD_HDL_TREE_HASH_MATCH=PASS;TREE_SHA256=%s\n' "$bd_tree_sha"

traversal_output_win="$authorized_root_win/../s3_guard_traversal_rejected"
run_fail_case traversal "$traversal_output_win" OUTPUT_DIR_TRAVERSAL_REJECTED
run_fail_case invalid_phase "$(cygpath -aw "$authorized_root/${prefix}_invalid_phase")" INVALID_PHASE invalid
run_fail_case invalid_mode "$(cygpath -aw "$authorized_root/${prefix}_invalid_mode")" INVALID_MODE guard invalid

existing_dir="$authorized_root/${prefix}_existing"
existing_dir_win="$(cygpath -aw "$existing_dir")"
if [[ -e "$existing_dir" || -L "$existing_dir" ]]; then
    printf '%s\n' 'PATH_GUARD_SELFTEST=FAIL;REASON=EXISTING_FIXTURE_COLLISION' >&2
    exit 2
fi
mkdir "$existing_dir"
run_fail_case existing "$existing_dir_win" OUTPUT_PATH_ALREADY_EXISTS

nested_output_win="$authorized_root_win/${prefix}_nested/child"
run_fail_case nested "$nested_output_win" OUTPUT_MUST_BE_DIRECT_CHILD_OF_AUTHORIZED_S3R04
run_fail_internal_case race_outside_root RACE_TARGET_OUTSIDE_AUTHORIZED_S3R04 \
    --internal-race-target-check "$vendor_root_win/ShouldNeverBeCreatedByPathGuardTest"

printf 'PATH_GUARD_SELFTEST=PASS;CASES=%s;VENDOR_COMMIT=%s;OUTPUT_ROOT=%s\n' \
    "$passed" fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327 "$authorized_root_win"
