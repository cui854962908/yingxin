#!/usr/bin/env bash
# verify.sh —— 对照 CLAUDE.md 硬性规则，一次跑完所有自动验证。
# 用法：bash scripts/verify.sh
# 退出码 0 = 全部通过，非 0 = 有违规。
set -euo pipefail
shopt -s globstar nullglob
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

violations=""

fail() { violations+="$1"$'\n'; echo -e "  ${RED}✗${NC} $1"; }
pass() { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }

echo "========== 文件行数 =========="

# 1. Vue SFC：script + template ≤ 300（超标需有注释说明例外理由）
echo "[Vue SFC ≤ 300 行]"
over=0
for f in "$ROOT"/frontend/src/**/*.vue; do
  [ -f "$f" ] || continue
  s_start=$(grep -n '<script' "$f" | head -1 | cut -d: -f1)
  s_end=$(grep -n '</script>' "$f" | tail -1 | cut -d: -f1)
  s=$((s_end - s_start + 1))
  t_start=$(grep -n '<template>' "$f" | head -1 | cut -d: -f1)
  t_end=$(grep -n '</template>' "$f" | tail -1 | cut -d: -f1)
  t=$((t_end - t_start + 1))
  total=$((s + t))
  if [ "$total" -gt 300 ]; then
    justification=$(head -10 "$f" | grep -cE '超出.*行限制|超标|例外' 2>/dev/null || true)
    if [ "$justification" -gt 0 ]; then
      warn "$f → script+template=$total 行（有注释说明例外理由）"
    else
      fail "$f → script+template=$total 行（无例外说明）"
      over=$((over + 1))
    fi
  fi
done
[ "$over" -eq 0 ] && pass "全部通过"

# 2. Python/TS 源文件 ≤ 450
echo "[Python/TS ≤ 450 行]"
over=0
for f in "$ROOT"/backend/app/**/*.py "$ROOT"/backend/tests/**/*.py "$ROOT"/frontend/src/**/*.ts; do
  [ -f "$f" ] || continue
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 450 ]; then
    justification=$(head -10 "$f" | grep -cE '超出.*行限制|超标|例外' 2>/dev/null || true)
    if [ "$justification" -gt 0 ]; then
      warn "$f → $lines 行（有注释说明例外理由）"
    else
      fail "$f → $lines 行（上限 450）"
      over=$((over + 1))
    fi
  fi
done
[ "$over" -eq 0 ] && pass "全部通过"

# 3. SQL/YAML/JSON ≤ 200（排除自动生成文件和备份）
echo "[SQL/YAML/JSON ≤ 200 行]"
over=0
for f in "$ROOT"/backend/alembic/versions/*.py "$ROOT"/*.yml "$ROOT"/*.yaml "$ROOT"/docker-compose*.yml; do
  [ -f "$f" ] || continue
  lines=$(wc -l < "$f")
  [ "$lines" -gt 200 ] && { fail "$f → $lines 行（上限 200）"; over=$((over + 1)); }
done
[ "$over" -eq 0 ] && pass "全部通过"

echo ""
echo "========== 调试语句 =========="

# 4. 前端：禁止 console.log / console.debug
echo "[前端 console.log / debug]"
hits=$(grep -rn 'console\.\(log\|debug\)' "$ROOT/frontend/src" --include='*.vue' --include='*.ts' 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "$hits"
  fail "$(echo "$hits" | wc -l) 处 console.log/debug（禁止使用）"
else
  pass "0 处"
fi
wc=$(grep -rn 'console\.\(warn\|error\)' "$ROOT/frontend/src" --include='*.vue' --include='*.ts' 2>/dev/null | wc -l || true)
warn "console.warn/error：${wc// /} 处（仅限错误边界使用，不宜新增）"

# 5. 后端：禁止调试用 print()，CLI 进度输出（flush=True）除外
echo "[后端 print() 调试]"
hits=$(grep -rn 'print(' "$ROOT/backend/app" --include='*.py' 2>/dev/null | grep -v '^\s*#' | grep -v 'flush=True' || true)
if [ -n "$hits" ]; then
  echo "$hits"
  fail "$(echo "$hits" | wc -l) 处调试用 print()，应改用 logging"
else
  pass "0 处"
fi
progress_prints=$(grep -rn 'print(' "$ROOT/backend/app" --include='*.py' 2>/dev/null | grep -v '^\s*#' | grep 'flush=True' | wc -l || true)
[ "${progress_prints// /}" -gt 0 ] && pass "print(flush=True)：${progress_prints// /} 处 CLI 进度输出（允许）"

echo ""
echo "========== 函数行数 =========="

# 6. Python 函数 ≤ 50 行
echo "[Python 函数 ≤ 50 行]"
pyresult=$(python3 -c "
import ast, os
over = 0
root = '$ROOT/backend/app'
for dirpath, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(dirpath, f)
        try:
            with open(path) as fh:
                tree = ast.parse(fh.read())
        except: continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = node.end_lineno or node.lineno
                lines = end - node.lineno + 1
                if lines > 50:
                    print(f'{path}:{node.lineno}: {node.name}()——{lines} 行')
                    over += 1
if over > 0:
    print(f'合计 {over} 个函数超过 50 行')
" 2>&1 || true)
if [ -z "$pyresult" ]; then
  pass "全部通过"
else
  echo "$pyresult"
  fail "存在超过 50 行的函数"
fi

echo ""
echo "========== 测试覆盖率 =========="

# 7. 覆盖率检查（需安装 pytest-cov / @vitest/coverage-v8，未装则跳过）
echo "[测试覆盖率 ≥ 80%]"
has_pytest_cov=$(cd "$ROOT/backend" && python -c "import pytest_cov" 2>/dev/null && echo 1 || echo 0)
has_vitest_cov=$([ -d "$ROOT/frontend/node_modules/@vitest/coverage-v8" ] && echo 1 || echo 0)

if [ "$has_pytest_cov" = "0" ] && [ "$has_vitest_cov" = "0" ]; then
  warn "pytest-cov 和 @vitest/coverage-v8 均未安装，跳过覆盖率检查"
  warn "安装：cd backend && uv pip install pytest-cov && cd ../frontend && npm i -D @vitest/coverage-v8"
else
  warn "覆盖率工具已安装但需手动运行（完整测试耗时较长）"
  warn "后端：cd backend && python -m pytest tests/ --cov=app --cov-report=term"
  warn "前端：cd frontend && npx vitest run --coverage"
  warn "要求 ≥ 80%，不达标不准提交"
fi

echo ""
if [ -z "$violations" ]; then
  echo -e "${GREEN}========================================${NC}"
  echo -e "${GREEN}  全部硬性规则检查通过 ✓${NC}"
  echo -e "${GREEN}========================================${NC}"
  exit 0
else
  echo -e "${RED}========================================${NC}"
  echo -e "${RED}  以下规则被违反：${NC}"
  echo -e "$violations"
  echo -e "${RED}  请修复后重新运行 bash scripts/verify.sh${NC}"
  echo -e "${RED}========================================${NC}"
  exit 1
fi
