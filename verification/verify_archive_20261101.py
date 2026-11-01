"""核验暂停归档的提交内容身份；不编译、不连接板卡、不修改文件。"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path, PurePosixPath


def git_blob(repo, commit, path):
    """从指定提交读取内容，避免工作区换行转换影响哈希。"""
    rel = PurePosixPath(path)
    if not path.startswith("archive/project-paused-20261101/") or rel.is_absolute() or ".." in rel.parts or "\\" in path or ":" in path:
        raise ValueError("归档路径越界或格式不合法")
    run = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), "cat-file", "blob", commit+":"+path], capture_output=True, check=False)
    if run.returncode:
        raise ValueError("提交中缺少文件："+path)
    return run.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--commit", default="HEAD")
    args = parser.parse_args()
    repo = Path(args.repo).resolve(strict=True)
    manifest_path = "archive/project-paused-20261101/manifest.json"
    try:
        doc = json.loads(git_blob(repo, args.commit, manifest_path).decode("utf-8"))
        if doc.get("hash_basis") != "commit_blob" or not doc.get("files"):
            raise ValueError("清单缺少 commit_blob 基座或文件列表")
        for item in doc["files"]:
            if item.get("hash_basis") != "commit_blob":
                raise ValueError("文件条目缺少 commit_blob 基座")
            payload = git_blob(repo, args.commit, item["path"])
            if len(payload) != item["bytes"] or hashlib.sha256(payload).hexdigest() != item["sha256"]:
                raise ValueError("内容身份不符："+item["path"])
        print(json.dumps({"status":"ARCHIVE_FILES_OK", "files":len(doc["files"]), "commit":args.commit, "meaning":"只核对提交内容身份，不代表功能或板级验收。"}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status":"FAIL", "reason":str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
