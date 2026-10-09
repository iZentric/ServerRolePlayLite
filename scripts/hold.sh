#!/usr/bin/env bash
pkill -f "java @unix_args" 2>/dev/null; pkill -f "bore local" 2>/dev/null
rm -f $HOME/hold-chain 2>/dev/null
echo "oprit" > /tmp/hold.txt
exit 0
