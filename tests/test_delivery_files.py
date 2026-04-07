from pathlib import Path
import re


def test_makefile_contains_expected_delivery_targets() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    makefile_content = (project_dir / "Makefile").read_text(encoding="utf-8")

    assert re.search(r"^demo:\s*$", makefile_content, re.MULTILINE)
    assert "$(PYTHON) main.py --config data/demo.yaml" in makefile_content
    assert re.search(r"^demos:\s*$", makefile_content, re.MULTILINE)
    assert "$(PYTHON) run_all_demos.py" in makefile_content
    assert re.search(r"^test:\s*$", makefile_content, re.MULTILINE)
    assert "\tpytest" in makefile_content or "\npytest\n" in makefile_content
    assert re.search(r"^web-backend:\s*$", makefile_content, re.MULTILINE)
    assert "$(PYTHON) -m uvicorn backend.app.main:app --reload --port 8000" in makefile_content
    assert re.search(r"^web-frontend:\s*$", makefile_content, re.MULTILINE)
    assert "\tcd frontend && npm run dev" in makefile_content


def test_project_status_document_mentions_acceptance_flow() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    status_content = (project_dir / "PROJECT_STATUS.md").read_text(encoding="utf-8")

    assert "当前项目状态" in status_content
    assert "快速验收步骤" in status_content
    assert "make demo" in status_content
    assert "make demos" in status_content
    assert "make test" in status_content
    assert "当前限制" in status_content
    assert "make web-backend" in status_content
    assert "make web-frontend" in status_content


def test_final_checklist_and_gitignore_cover_release_cleanup() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    checklist_content = (project_dir / "FINAL_CHECKLIST.md").read_text(encoding="utf-8")
    gitignore_content = (project_dir / ".gitignore").read_text(encoding="utf-8")

    assert "项目结构检查" in checklist_content
    assert "依赖安装检查" in checklist_content
    assert "基线 demo 运行检查" in checklist_content
    assert "批量 demo 检查" in checklist_content
    assert "测试通过检查" in checklist_content
    assert "提交前建议清理项" in checklist_content
    assert "outputs/" in gitignore_content
    assert ".pytest_cache/" in gitignore_content
    assert "__pycache__/" in gitignore_content


def test_readme_mentions_web_run_entrypoints() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    readme_content = (project_dir / "README.md").read_text(encoding="utf-8")

    assert "make web-backend" in readme_content
    assert "make web-frontend" in readme_content
    assert "http://localhost:8000/health" in readme_content
    assert "http://localhost:3000" in readme_content
    assert "建议启动顺序" in readme_content


def test_testing_doc_describes_automation_and_smoke_boundaries() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    testing_content = (project_dir / "TESTING.md").read_text(encoding="utf-8")

    assert "已自动化覆盖的部分" in testing_content
    assert "Web 当前的轻量验证方式" in testing_content
    assert "当前未自动化覆盖的部分" in testing_content
    assert "pytest -q" in testing_content
    assert "make web-backend" in testing_content
    assert "make web-frontend" in testing_content
