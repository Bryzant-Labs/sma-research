#!/usr/bin/env bash
until ssh -o BatchMode=yes -i ~/.ssh/id_ed25519_vastai root@ssh2.vast.ai -p 21610 "grep -q DEPS_DONE /root/pxm_env_setup.log 2>/dev/null"; do
  sleep 15
done
echo "PXM env build complete on asxm"
