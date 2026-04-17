#!/usr/bin/env bash
until ssh -o BatchMode=yes -i ~/.ssh/id_ed25519_vastai root@ssh2.vast.ai -p 21610 "grep -q PYG_DONE /root/torch_install.log 2>/dev/null"; do
  sleep 20
done
echo "torch + pyg install done on asxm"
