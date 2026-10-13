"""核对原厂unloadhw不会改变已保存的映射证据对象。"""
from pathlib import Path
import copy
source=Path(__file__).with_name("review_full_sdk.py").read_text(encoding="utf-8")
source=source.replace("sdk_fixture_r03","sdk_fixture_r04").replace("full_sdk_cases_result.json","snapshot_sdk_cases_result.json")
source=source.replace('exec(compile(source,str(Path(__file__)),"exec"))','''source=source.replace('case.register();case.clear()', 'case.register();before_regions=copy.deepcopy(case.record["debug_memory_map"]["sdk_regions"]);before_entries=copy.deepcopy(case.record["debug_memory_map"]["sdk_entries"]);case.clear();assert case.record["debug_memory_map"]["sdk_regions"]==before_regions;assert case.record["debug_memory_map"]["sdk_entries"]==before_entries')
source=source.replace('"official_full_set_hsi_load_unload_success"','"official_full_sdk_snapshot_preserved_after_unload"')
exec(compile(source,str(Path(__file__)),"exec"))''')
exec(compile(source,str(Path(__file__)),"exec"))
