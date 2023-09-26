# library

## Testing
1. Run service `python3 examples/simple_service.py`
2. Test checker `python3 examples/simple_checker.py test`

example output: 
```
INFO:checker:iteration:1
INFO:checker:ping => pong
INFO:checker:put:example(kmktdbCYRtMJuBxfPJryzDTL) => 0
INFO:checker:get:example(0) => kmktdbCYRtMJuBxfPJryzDTL
INFO:checker:exploit:sql => exploitable
INFO:checker:exploit:rce => exploitable
INFO:checker:iteration:2
INFO:checker:ping => pong
INFO:checker:put:example(AZoodDXcDmdCVMNEyjTcAMyE) => 1
INFO:checker:get:example(1) => AZoodDXcDmdCVMNEyjTcAMyE
INFO:checker:exploit:sql => exploitable
INFO:checker:exploit:rce => exploitable
```