#!/usr/bin/env bash
set -euo pipefail

IMAGE="${SAGE_DOCKER_IMAGE:-sagemath/sagemath:latest}"
MODE="check"

for arg in "$@"; do
  case "$arg" in
    --check) MODE="check" ;;
    --pull) MODE="pull" ;;
    --test) MODE="test" ;;
    --micromamba) MODE="micromamba" ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

echo "host=$(hostname)"
echo "mode=$MODE"

sage_ok() {
  "$1" -python -c 'import sage.all' >/dev/null 2>&1
}

if command -v sage >/dev/null 2>&1 && sage_ok "$(command -v sage)"; then
  echo "native_sage=$(command -v sage)"
  sage -v || true
  exit 0
fi

for candidate in "$HOME/mamba/envs/sage/bin/sage" "$HOME/micromamba/envs/sage/bin/sage" "$HOME/.local/bin/sage" "$HOME/bin/sage"; do
  if [ -x "$candidate" ] && sage_ok "$candidate"; then
    echo "native_sage=$candidate"
    "$candidate" -v || true
    exit 0
  fi
done

echo "native_sage=missing"

if [ "$MODE" = "micromamba" ]; then
  if ! command -v micromamba >/dev/null 2>&1; then
    if command -v brew >/dev/null 2>&1; then
      brew install micromamba
    else
      echo "micromamba=missing and brew=missing"
      exit 1
    fi
  fi
  mkdir -p "$HOME/mamba/envs" "$HOME/bin"
  micromamba create -y -p "$HOME/mamba/envs/sage" -c conda-forge sage
  cat > "$HOME/bin/sage" <<'EOF'
#!/usr/bin/env bash
exec "$HOME/mamba/envs/sage/bin/sage" "$@"
EOF
  chmod +x "$HOME/bin/sage"
  "$HOME/mamba/envs/sage/bin/sage" -v
  exit 0
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker=missing"
  exit 1
fi

echo "docker=$(command -v docker)"

if [ "$MODE" = "pull" ]; then
  echo "pulling $IMAGE"
  docker pull "$IMAGE"
fi

if docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "docker_sage_image=present:$IMAGE"
  if [ "$MODE" = "test" ] || [ "$MODE" = "pull" ]; then
    docker run --rm -e HOME=/tmp "$IMAGE" sage -v
  fi
  exit 0
fi

echo "docker_sage_image=missing:$IMAGE"
echo "run: bash _compute_queue/scripts/install_sage_backend.sh --pull"
exit 1
