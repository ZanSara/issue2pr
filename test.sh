  FEEDBACK="no feedback"
  git checkout -b fix/44
  loops=0
  while [ $loops -le 10 ]
  do
    loops=$((loops + 1))
    echo "script_output=$(python convert_issue_to_pr.py \
        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 \
        '{"body":"## Problem\r\nThe function should sum the two numbers but instead it subtracts them.\r\n\r\n## Test\r\n```python\r\ndef test_add_numbers_together():\r\n    assert add_numbers_together(1, 2) == 3\r\n```\r\n## Environment\r\n- Operating system: Ubuntu 22.04\r\n- Python version: 3.11\r\n","labels":[],"title":"issue"}' \
        "$FEEDBACK" \
        '.' \
    )" >> changes.patch
    cat changes.patch

    ERROR=$(git apply --ignore-space-change --ignore-whitespace changes.patch 2>&1 >/dev/null)
    if $ERROR; then
        FEEDBACK=$ERROR
    else
        echo "Patch applied"
        rm changes.patch
        break
    fi
  done
  git branch -d fix/44
