# API接口文档

本文档包含从网站抓取的API接口信息，经过处理和格式化。

## 目录

1. [http://api.biyingapi.com/hslt/list/您的licence](#http://api.biyingapi.com/hslt/list/您的licence)
2. [http://api.biyingapi.com/hslt/new/您的licence](#http://api.biyingapi.com/hslt/new/您的licence)
3. [http://api.biyingapi.com/hszg/list/您的licence](#http://api.biyingapi.com/hszg/list/您的licence)
4. [http://api.biyingapi.com/hszg/gg/指数、行业、概念代码/您的licence](#http://api.biyingapi.com/hszg/gg/指数、行业、概念代码/您的licence)
5. [http://api.biyingapi.com/hszg/zg/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hszg/zg/股票代码(如000001)/您的licence)
6. [http://api.biyingapi.com/hslt/ztgc/日期(如2020-01-15)/您的licence](#http://api.biyingapi.com/hslt/ztgc/日期(如2020-01-15)/您的licence)
7. [http://api.biyingapi.com/hslt/dtgc/日期(如2020-01-15)/您的licence](#http://api.biyingapi.com/hslt/dtgc/日期(如2020-01-15)/您的licence)
8. [http://api.biyingapi.com/hslt/qsgc/日期(如2020-01-15)/您的licence](#http://api.biyingapi.com/hslt/qsgc/日期(如2020-01-15)/您的licence)
9. [http://api.biyingapi.com/hslt/cxgc/日期(如2020-01-15)/您的licence](#http://api.biyingapi.com/hslt/cxgc/日期(如2020-01-15)/您的licence)
10. [http://api.biyingapi.com/hslt/zbgc/日期(如2020-01-15)/您的licence](#http://api.biyingapi.com/hslt/zbgc/日期(如2020-01-15)/您的licence)
11. [http://api.biyingapi.com/hscp/gsjj/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/gsjj/股票代码(如000001)/您的licence)
12. [http://api.biyingapi.com/hscp/sszs/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/sszs/股票代码(如000001)/您的licence)
13. [http://api.biyingapi.com/hscp/ljgg/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/ljgg/股票代码(如000001)/您的licence)
14. [http://api.biyingapi.com/hscp/ljds/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/ljds/股票代码(如000001)/您的licence)
15. [http://api.biyingapi.com/hscp/ljjj/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/ljjj/股票代码(如000001)/您的licence)
16. [http://api.biyingapi.com/hscp/jnfh/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/jnfh/股票代码(如000001)/您的licence)
17. [http://api.biyingapi.com/hscp/jnzf/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/jnzf/股票代码(如000001)/您的licence)
18. [http://api.biyingapi.com/hscp/jjxs/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/jjxs/股票代码(如000001)/您的licence)
19. [http://api.biyingapi.com/hscp/jdlr/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/jdlr/股票代码(如000001)/您的licence)
20. [http://api.biyingapi.com/hscp/jdxj/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/jdxj/股票代码(如000001)/您的licence)
21. [http://api.biyingapi.com/hscp/yjyg/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/yjyg/股票代码(如000001)/您的licence)
22. [http://api.biyingapi.com/hscp/cwzb/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/cwzb/股票代码(如000001)/您的licence)
23. [http://api.biyingapi.com/hscp/sdgd/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/sdgd/股票代码(如000001)/您的licence)
24. [http://api.biyingapi.com/hscp/ltgd/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/ltgd/股票代码(如000001)/您的licence)
25. [http://api.biyingapi.com/hscp/gdbh/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/gdbh/股票代码(如000001)/您的licence)
26. [http://api.biyingapi.com/hscp/jjcg/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hscp/jjcg/股票代码(如000001)/您的licence)
27. [http://api.biyingapi.com/hsrl/ssjy/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hsrl/ssjy/股票代码(如000001)/您的licence)
28. [http://api.biyingapi.com/hsrl/zbjy/股票代码(如000001)/您的licence](#http://api.biyingapi.com/hsrl/zbjy/股票代码(如000001)/您的licence)
29. [https://api.biyingapi.com/hsstock/real/time/股票代码/证书您的licence](#https://api.biyingapi.com/hsstock/real/time/股票代码/证书您的licence)
30. [https://api.biyingapi.com/hsstock/real/five/股票代码/证书您的licence](#https://api.biyingapi.com/hsstock/real/five/股票代码/证书您的licence)
31. [http://api.biyingapi.com/hsrl/ssjy_more/您的licence?stock_codes=股票代码1,股票代码2……股票代码20](#http://api.biyingapi.com/hsrl/ssjy_more/您的licence?stock_codes=股票代码1,股票代码2……股票代码20)
32. [http://api.biyingapi.com/hsstock/history/transaction/股票代码(如000001)/您的licence?st=开始时间&et=结束时间&lt=最新条数](#http://api.biyingapi.com/hsstock/history/transaction/股票代码(如000001)/您的licence?st=开始时间&et=结束时间&lt=最新条数)
33. [https://api.biyingapi.com/hsstock/latest/股票代码.市场（如000001.SZ）/分时级别(如d)/除权方式/您的licence?lt=最新条数(如3)](#https://api.biyingapi.com/hsstock/latest/股票代码.市场（如000001.SZ）/分时级别(如d)/除权方式/您的licence?lt=最新条数(如3))
34. [https://api.biyingapi.com/hsstock/history/股票代码.市场（如000001.SZ）/分时级别(如d)/除权方式/您的licence?st=开始时间(如20240601)&et=结束时间(如20250430)&lt=最新条数(如100)](#https://api.biyingapi.com/hsstock/history/股票代码.市场（如000001.SZ）/分时级别(如d)/除权方式/您的licence?st=开始时间(如20240601)&et=结束时间(如20250430)&lt=最新条数(如100))
35. [http://api.biyingapi.com/hsstock/stopprice/history/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/stopprice/history/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
36. [http://api.biyingapi.com/hsstock/indicators/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/indicators/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
37. [http://api.biyingapi.com/hsstock/instrument/股票代码（如000001.SZ）/您的licence](#http://api.biyingapi.com/hsstock/instrument/股票代码（如000001.SZ）/您的licence)
38. [http://api.biyingapi.com/hsstock/financial/balance/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/financial/balance/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
39. [http://api.biyingapi.com/hsstock/financial/income/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/financial/income/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
40. [http://api.biyingapi.com/hsstock/financial/cashflow/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/financial/cashflow/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
41. [http://api.biyingapi.com/hsstock/financial/pershareindex/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/financial/pershareindex/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
42. [http://api.biyingapi.com/hsstock/financial/capital/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/financial/capital/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
43. [http://api.biyingapi.com/hsstock/financial/topholder/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/financial/topholder/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
44. [http://api.biyingapi.com/hsstock/financial/flowholder/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/financial/flowholder/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
45. [http://api.biyingapi.com/hsstock/financial/hm/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间](#http://api.biyingapi.com/hsstock/financial/hm/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间)
46. [http://api.biyingapi.com/hsstock/history/macd/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数](#http://api.biyingapi.com/hsstock/history/macd/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数)
47. [http://api.biyingapi.com/hsstock/history/ma/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数](#http://api.biyingapi.com/hsstock/history/ma/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数)
48. [http://api.biyingapi.com/hsstock/history/boll/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数](#http://api.biyingapi.com/hsstock/history/boll/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数)
49. [http://api.biyingapi.com/hsstock/history/kdj/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数](#http://api.biyingapi.com/hsstock/history/kdj/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数)

## 接口详情

### http://api.biyingapi.com/hslt/list/您的licence

API接口：http://api.biyingapi.com/hslt/list/biyinglicence

### http://api.biyingapi.com/hslt/new/您的licence

API接口：http://api.biyingapi.com/hslt/new/biyinglicence

### http://api.biyingapi.com/hszg/list/您的licence

API接口：http://api.biyingapi.com/hszg/list/biyinglicence

### http://api.biyingapi.com/hszg/gg/指数、行业、概念代码/您的licence

API接口：http://api.biyingapi.com/hszg/gg/sw_sysh/biyinglicence

### http://api.biyingapi.com/hszg/zg/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hszg/zg/000001/biyinglicence

### http://api.biyingapi.com/hslt/ztgc/日期(如2020-01-15)/您的licence

API接口：http://api.biyingapi.com/hslt/ztgc/2024-01-10/biyinglicence

### http://api.biyingapi.com/hslt/dtgc/日期(如2020-01-15)/您的licence

API接口：http://api.biyingapi.com/hslt/dtgc/2024-01-10/biyinglicence

### http://api.biyingapi.com/hslt/qsgc/日期(如2020-01-15)/您的licence

API接口：http://api.biyingapi.com/hslt/qsgc/2024-01-10/biyinglicence

### http://api.biyingapi.com/hslt/cxgc/日期(如2020-01-15)/您的licence

API接口：http://api.biyingapi.com/hslt/cxgc/2024-01-10/biyinglicence

### http://api.biyingapi.com/hslt/zbgc/日期(如2020-01-15)/您的licence

API接口：http://api.biyingapi.com/hslt/zbgc/2024-01-10/biyinglicence

### http://api.biyingapi.com/hscp/gsjj/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/gsjj/000001/biyinglicence

### http://api.biyingapi.com/hscp/sszs/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/sszs/000001/biyinglicence

### http://api.biyingapi.com/hscp/ljgg/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/ljgg/000001/biyinglicence

### http://api.biyingapi.com/hscp/ljds/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/ljds/000001/biyinglicence

### http://api.biyingapi.com/hscp/ljjj/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/ljjj/000001/biyinglicence

### http://api.biyingapi.com/hscp/jnfh/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/jnfh/000001/biyinglicence

### http://api.biyingapi.com/hscp/jnzf/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/jnzf/000001/biyinglicence

### http://api.biyingapi.com/hscp/jjxs/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/jjxs/000001/biyinglicence

### http://api.biyingapi.com/hscp/jdlr/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/jdlr/000001/biyinglicence

### http://api.biyingapi.com/hscp/jdxj/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/jdxj/000001/biyinglicence

### http://api.biyingapi.com/hscp/yjyg/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/yjyg/000001/biyinglicence

### http://api.biyingapi.com/hscp/cwzb/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/cwzb/000001/biyinglicence

### http://api.biyingapi.com/hscp/sdgd/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/sdgd/000001/biyinglicence

### http://api.biyingapi.com/hscp/ltgd/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/ltgd/000001/biyinglicence

### http://api.biyingapi.com/hscp/gdbh/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/gdbh/000001/biyinglicence

### http://api.biyingapi.com/hscp/jjcg/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hscp/jjcg/000001/biyinglicence

### http://api.biyingapi.com/hsrl/ssjy/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hsrl/ssjy/000001/biyinglicence

### http://api.biyingapi.com/hsrl/zbjy/股票代码(如000001)/您的licence

API接口：http://api.biyingapi.com/hsrl/zbjy/000001/biyinglicence

### https://api.biyingapi.com/hsstock/real/time/股票代码/证书您的licence

API接口：https://api.biyingapi.com/hsstock/real/time/000001/biyinglicence

### https://api.biyingapi.com/hsstock/real/five/股票代码/证书您的licence

API接口：https://api.biyingapi.com/hsstock/real/five/000001/biyinglicence

### http://api.biyingapi.com/hsrl/ssjy_more/您的licence?stock_codes=股票代码1,股票代码2……股票代码20

API接口：http://api.biyingapi.com/hsrl/ssjy_more/biyinglicence?stock_codes=000001,000002,000004

### http://api.biyingapi.com/hsstock/history/transaction/股票代码(如000001)/您的licence?st=开始时间&et=结束时间&lt=最新条数

API接口：http://api.biyingapi.com/hsstock/history/transaction/000001/biyinglicence

### https://api.biyingapi.com/hsstock/latest/股票代码.市场（如000001.SZ）/分时级别(如d)/除权方式/您的licence?lt=最新条数(如3)

API接口：https://api.biyingapi.com/hsstock/latest/000001.SZ/d/n/biyinglicence?lt=1

### https://api.biyingapi.com/hsstock/history/股票代码.市场（如000001.SZ）/分时级别(如d)/除权方式/您的licence?st=开始时间(如20240601)&et=结束时间(如20250430)&lt=最新条数(如100)

API接口：https://api.biyingapi.com/hsstock/history/000001.SZ/d/n/biyinglicence?st=20250101&et=20250430&lt=100

### http://api.biyingapi.com/hsstock/stopprice/history/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/stopprice/history/000001.SZ/biyinglicence?st=20240501&et=20240601

### http://api.biyingapi.com/hsstock/indicators/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/indicators/600519.SH/biyinglicence

### http://api.biyingapi.com/hsstock/instrument/股票代码（如000001.SZ）/您的licence

API接口：http://api.biyingapi.com/hsstock/instrument/000001.SZ/biyinglicence

### http://api.biyingapi.com/hsstock/financial/balance/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/financial/balance/600519.SH/biyinglicence?st=20230330&et=20230630

### http://api.biyingapi.com/hsstock/financial/income/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/financial/income/600519.SH/biyinglicence?st=20230330&et=20230630

### http://api.biyingapi.com/hsstock/financial/cashflow/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/financial/cashflow/600519.SH/biyinglicence?st=20230330&et=20230630

### http://api.biyingapi.com/hsstock/financial/pershareindex/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/financial/pershareindex/600519.SH/biyinglicence?st=20230330&et=20230630

### http://api.biyingapi.com/hsstock/financial/capital/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/financial/capital/600519.SH/biyinglicence?st=20230330&et=20230630

### http://api.biyingapi.com/hsstock/financial/topholder/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/financial/topholder/600519.SH/biyinglicence?st=20230330&et=20230630

### http://api.biyingapi.com/hsstock/financial/flowholder/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/financial/flowholder/600519.SH/biyinglicence?st=20230330&et=20230630

### http://api.biyingapi.com/hsstock/financial/hm/股票代码（如000001.SZ）/您的licence?st=开始时间&et=结束时间

API接口：http://api.biyingapi.com/hsstock/financial/hm/600519.SH/biyinglicence?st=20230330&et=20230630

### http://api.biyingapi.com/hsstock/history/macd/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数

API接口：http://api.biyingapi.com/hsstock/history/macd/000001.SZ/d/n/biyinglicence

### http://api.biyingapi.com/hsstock/history/ma/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数

API接口：http://api.biyingapi.com/hsstock/history/ma/000001.SZ/d/n/biyinglicence

### http://api.biyingapi.com/hsstock/history/boll/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数

API接口：http://api.biyingapi.com/hsstock/history/boll/000001.SZ/d/n/biyinglicence

### http://api.biyingapi.com/hsstock/history/kdj/股票代码(如000001.SZ)/分时级别(如d)/除权类型(如n)/您的licence?st=开始时间&et=结束时间&lt=最新条数

API接口：http://api.biyingapi.com/hsstock/history/kdj/000001.SZ/d/n/biyinglicence

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

返回字段映射：
字段名称	数据类型	字段说明

