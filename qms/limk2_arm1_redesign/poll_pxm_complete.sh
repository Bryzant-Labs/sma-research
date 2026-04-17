#!/usr/bin/env bash
until ssh -o BatchMode=yes -i ~/.ssh/id_ed25519_vastai root@ssh2.vast.ai -p 21610 "test -f /root/results_limk2_arm1/.complete 2>/dev/null"; do
  sleep 25
done
echo "PXM all 3 strategies complete"
ssh -o BatchMode=yes -i ~/.ssh/id_ed25519_vastai root@ssh2.vast.ai -p 21610 "tail -20 /root/results_limk2_arm1/run.log"
