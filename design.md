文档信息
项目内容文档版本V1.0关联需求文档交易策略系统需求文档 V4.0更新日期2026-04-21系统名称双仓位交易策略看板技术栈Vue 3 + Django + MySQL + Tushare
--------------------------------------------------------------------------------
目录
1.系统功能总览
2.用户认证模块
3.数据管理模块
4.大盘状态判断模块
5.ETF策略模块
6.个股策略模块
7.箱体分析模块
8.做T管理模块
9.风险管理模块
10.策略配置模块
11.报表分析模块
12.表结构设计
--------------------------------------------------------------------------------
一、系统功能总览
1.1 功能模块清单
序号模块名称功能描述优先级1用户认证注册、登录、Token管理P02数据管理Tushare数据同步、技术指标计算P03大盘状态判断市场状态识别、事件修正、仓位建议P04ETF策略ETF买卖建议、持仓管理P05个股策略个股开仓/平仓、关键点识别P16箱体分析箱体识别、位置判断、操作建议P17做T管理做T记录、成功率监控P18风险管理止损计算、回撤监控、连续亏损保护P09策略配置阈值参数配置、个性化设置P110报表分析交易统计、盈亏分析P2
1.2 功能层次图
text
交易策略系统
│
├── 用户认证层
│   ├── 用户注册
│   ├── 用户登录
│   └── Token刷新
│
├── 数据层
│   ├── Tushare数据同步
│   ├── 技术指标计算
│   ├── 事件日历维护
│   └── 数据完整性检查
│
├── 策略计算层
│   ├── 大盘状态判断
│   │   ├── 技术状态计算
│   │   ├── 大周期状态计算
│   │   ├── 事件修正计算
│   │   └── 综合状态输出
│   ├── 关键点识别
│   │   ├── 突破关键点
│   │   ├── 回撤关键点
│   │   ├── 连续关键点
│   │   └── 反转关键点
│   └── 箱体分析
│       ├── 箱体识别
│       ├── 位置判断
│       └── 操作建议
│
├── 业务操作层
│   ├── ETF策略
│   │   ├── 买入建议
│   │   ├── 卖出建议
│   │   └── 持仓管理
│   ├── 个股策略
│   │   ├── 开仓管理
│   │   ├── 平仓管理
│   │   ├── 止损调整
│   │   └── 金字塔加仓
│   └── 做T管理
│       ├── 做T记录
│       ├── 成功率统计
│       └── 自动暂停
│
├── 风控层
│   ├── 单笔风险控制
│   ├── 连续亏损保护
│   ├── 回撤熔断
│   └── 仓位上限控制
│
└── 报表层
    ├── 交易统计
    ├── 盈亏分析
    └── 策略绩效
--------------------------------------------------------------------------------
二、用户认证模块
2.1 功能清单
功能编号功能名称功能描述输入输出AUTH-01用户注册新用户注册账号用户名、密码、邮箱注册结果AUTH-02用户登录用户登录获取Token用户名、密码Token、用户信息AUTH-03Token刷新刷新过期的TokenRefresh Token新Access TokenAUTH-04用户登出用户登出Token登出结果AUTH-05修改密码修改用户密码旧密码、新密码修改结果AUTH-06获取用户信息获取当前用户信息Token用户信息
2.2 功能细节
AUTH-01 用户注册
项目说明触发方式用户点击注册按钮前置条件未登录状态后置动作创建用户记录，返回登录页异常处理用户名已存在、密码格式错误、邮箱格式错误
AUTH-02 用户登录
项目说明触发方式用户点击登录按钮前置条件未登录状态后置动作生成JWT Token，跳转主页异常处理用户名不存在、密码错误、账户被锁定
2.3 涉及表结构
users_user
字段名类型说明idINT主键usernameVARCHAR(150)用户名，唯一passwordVARCHAR(128)加密密码emailVARCHAR(254)邮箱is_activeBOOLEAN是否激活last_loginDATETIME最后登录时间created_atDATETIME创建时间
users_userprofile
字段名类型说明idINT主键user_idINT关联用户IDtotal_capitalDECIMAL(15,2)总资金tushare_tokenVARCHAR(100)Tushare TokenthemeVARCHAR(20)主题：light/darkcreated_atDATETIME创建时间updated_atDATETIME更新时间
--------------------------------------------------------------------------------
三、数据管理模块
3.1 功能清单
功能编号功能名称功能描述输入输出DATA-01同步指数数据从Tushare同步指数日线数据指数代码、日期范围同步记录数DATA-02同步个股数据从Tushare同步个股日线数据股票代码、日期范围同步记录数DATA-03同步概念板块从Tushare同步概念板块数据概念名称同步记录数DATA-04计算技术指标计算RSI、MACD、OBV等指标日期范围指标记录DATA-05自动同步任务每日定时自动同步最新数据无同步结果DATA-06数据完整性检查检查数据是否完整，缺失则补录日期范围缺失数据列表DATA-07事件日历维护维护政策窗口、财报季等事件事件信息维护结果
3.2 功能细节
DATA-01 同步指数数据
项目说明触发方式用户手动点击同步 / 定时任务支持指数创业板指(399006.SZ)、上证指数(000001.SH)同步字段日期、开盘价、最高价、最低价、收盘价、成交量、成交额数据处理新数据插入，已存在数据更新同步频率每日收盘后自动同步（15:30）异常处理网络超时重试3次，记录失败日志
DATA-04 计算技术指标
项目说明触发方式数据同步后自动触发 / 手动触发计算指标20日涨跌幅、14日RSI、5/20/60日均线、OBV、量比、MACD计算周期每日计算存储方式计算结果存入技术指标表异常处理数据不足时跳过，记录警告日志
DATA-05 自动同步任务
项目说明触发方式Celery Beat定时任务执行时间每日15:30（收盘后）执行内容同步指数数据、同步自选股数据、计算技术指标、更新大盘状态失败处理重试3次，仍失败则发送通知
3.3 涉及表结构
market_marketdata
字段名类型说明idINT主键dateDATE交易日期index_codeVARCHAR(20)指数代码openDECIMAL(10,4)开盘价highDECIMAL(10,4)最高价lowDECIMAL(10,4)最低价closeDECIMAL(10,4)收盘价volumeBIGINT成交量amountBIGINT成交额created_atDATETIME创建时间
market_technicalindicators
字段名类型说明idINT主键market_data_idINT关联市场数据IDchange_20dDECIMAL(10,4)20日涨跌幅(%)rsi_14DECIMAL(10,4)14日RSIma_5DECIMAL(10,4)5日均线ma_20DECIMAL(10,4)20日均线ma_60DECIMAL(10,4)60日均线obvBIGINTOBV值obv_trendVARCHAR(20)OBV趋势volume_ratioDECIMAL(10,4)量比divergenceVARCHAR(20)背离状态macd_difDECIMAL(10,4)MACD DIFmacd_deaDECIMAL(10,4)MACD DEAmacd_barDECIMAL(10,4)MACD柱created_atDATETIME创建时间
strategy_eventcalendar
字段名类型说明idINT主键event_nameVARCHAR(100)事件名称event_typeVARCHAR(20)类型：政策/财报/长假/美联储/LPRstart_dateDATE开始日期end_dateDATE结束日期correction_valueDECIMAL(5,2)修正值yearINT年份descriptionVARCHAR(200)描述created_atDATETIME创建时间
sync_synclog
字段名类型说明idINT主键sync_typeVARCHAR(20)同步类型：index/stock/concepttarget_codeVARCHAR(20)目标代码start_dateDATE开始日期end_dateDATE结束日期synced_countINT同步记录数statusVARCHAR(20)状态：success/failederror_messageTEXT错误信息created_atDATETIME创建时间
--------------------------------------------------------------------------------
四、大盘状态判断模块
4.1 功能清单
功能编号功能名称功能描述输入输出STATE-01计算技术状态根据指标计算技术状态技术指标底部区/震荡区/上涨区/陷阱区STATE-02计算大周期状态根据指标计算大周期状态技术指标主升浪/正常趋势/赶顶期/震荡期/下跌期STATE-03计算事件修正根据当前日期计算事件修正当前日期修正值、活跃事件列表STATE-04计算主要趋势根据均线和指数验证判断主要趋势均线数据、指数对比牛市/震荡/熊市STATE-05计算最终状态综合技术状态和事件修正技术状态、事件修正最终状态、仓位上限STATE-06获取操作建议根据最终状态生成操作建议最终状态ETF建议、个股建议STATE-07分级离场判断判断是否触发分级离场信号价格、RSI、均线离场级别
4.2 功能细节
STATE-01 计算技术状态
项目说明判断逻辑按优先级从高到低判断：陷阱区 > 底部区 > 上涨区 > 震荡区陷阱区条件过去20日最大涨幅>8% 且 最近5日振幅<3% 且 成交量斜度持续下降>5日底部区条件20日跌幅<-8%且RSI<35 或 20日跌幅<-12% 或 RSI<25上涨区条件20日涨幅>5% 或 RSI>70震荡区条件不满足上述条件且20日涨跌幅在-5%到+5%之间计算频率每日收盘后自动计算
STATE-02 计算大周期状态
项目说明判断逻辑主升浪 > 赶顶期 > 正常趋势 > 下跌期 > 震荡期主升浪条件20日涨幅>10% 且 RSI>65 且 沿5日线上涨赶顶期条件20日涨幅>10% 且 出现顶背离正常趋势条件20日涨幅3%-10% 且 RSI 50-65下跌期条件20日跌幅>5% 或 跌破60日线震荡期条件不满足上述条件
STATE-03 计算事件修正
项目说明修正幅度上调一级(+1)、上调半级(+0.5)、下调一级(-1)、下调半级(-0.5)事件优先级政策窗口 > 美联储 > 财报季 > LPR > 长假修正叠加多个事件同时发生时，按优先级取主要修正，叠加累加但限制在-2到2范围计算频率每日自动计算
STATE-07 分级离场判断
项目说明一级离场出现顶背离（价格新高，RSI未新高），卖出1/3二级离场跌破10日线，再卖出1/3三级离场跌破20日线 或 5日线下穿20日线，清仓剩余计算频率每日自动计算
4.3 涉及表结构
strategy_marketstate
字段名类型说明idINT主键user_idINT用户IDdateDATE日期tech_stateVARCHAR(20)技术状态major_trendVARCHAR(20)主要趋势cycle_stateVARCHAR(20)大周期状态event_correctionVARCHAR(20)事件修正final_stateVARCHAR(20)最终状态max_positionINT建议仓位上限(%)etf_actionVARCHAR(50)ETF建议动作individual_actionVARCHAR(50)个股建议动作exit_levelINT离场级别(1/2/3)exit_reasonVARCHAR(100)离场原因created_atDATETIME创建时间
--------------------------------------------------------------------------------
五、ETF策略模块
5.1 功能清单
功能编号功能名称功能描述输入输出ETF-01获取ETF建议根据大盘状态获取ETF操作建议大盘状态买入/持有/卖出/清仓ETF-02记录ETF持仓记录ETF持仓信息买入日期、买入价、数量持仓记录ETF-03更新ETF持仓更新ETF持仓（卖出、加仓）操作类型、价格、数量更新结果ETF-04计算ETF止损根据主升浪状态计算止损位当前状态、买入价止损价ETF-05获取分批买入建议根据底部区判断分批买入时机当前价格、已持仓比例买入建议
5.2 功能细节
ETF-01 获取ETF建议
项目说明建议映射底部区→买入；震荡区→持有；上涨区→持有/分批卖出；主升浪→坚定持有；赶顶期→分批卖出；陷阱区→只卖不买；下跌期→清仓输出内容建议动作、建议仓位、止损位、目标位更新频率每日更新
ETF-05 获取分批买入建议
项目说明第一批买入条件进入底部区，买入25%总资金第二批买入条件已买入第一批，且价格继续下跌>5%第三批买入条件极端超跌（20日跌幅<-12%），买入剩余部分买入限制总ETF仓位不超过50%
5.3 涉及表结构
position_position
字段名类型说明idINT主键user_idINT用户IDsymbolVARCHAR(20)代码(如159915)nameVARCHAR(50)名称typeVARCHAR(20)类型：etf/individuallogicVARCHAR(20)逻辑：trend/box/short_termbuy_dateDATE买入日期buy_priceDECIMAL(10,4)买入价quantityINT数量stop_lossDECIMAL(10,4)止损价target_priceDECIMAL(10,4)目标价statusVARCHAR(20)状态：holding/selling/soldcreated_atDATETIME创建时间updated_atDATETIME更新时间
position_transaction
字段名类型说明idINT主键user_idINT用户IDposition_idINT关联持仓IDdateDATE交易日期directionVARCHAR(10)方向：buy/sellpriceDECIMAL(10,4)成交价quantityINT数量amountDECIMAL(15,2)金额feeDECIMAL(10,4)手续费logic_typeVARCHAR(50)逻辑类型created_atDATETIME创建时间
--------------------------------------------------------------------------------
六、个股策略模块
6.1 功能清单
功能编号功能名称功能描述输入输出STOCK-01识别关键点识别个股关键点信号个股K线数据关键点类型、强度STOCK-02开仓检查检查是否满足开仓条件个股代码、关键点信号是否允许开仓STOCK-03创建持仓创建个股持仓记录买入信息、止损位持仓记录STOCK-04更新持仓价格更新持仓当前价，计算盈亏个股代码、当前价更新后持仓STOCK-05检查止损检查是否触发止损持仓记录、当前价止损提醒STOCK-06检查止盈检查是否触发止盈持仓记录、当前价止盈提醒STOCK-07金字塔加仓建议判断是否可加仓持仓记录、当前价加仓建议STOCK-08平仓平仓操作持仓ID、卖出价平仓结果
6.2 功能细节
STOCK-01 识别关键点
项目说明突破关键点放量(量比>1.5)突破前期盘整区间上沿，强度：强(量比>2)/中(量比1.5-2)自然回撤关键点上升趋势中回调前波段1/3-1/2，缩量后放量启动，强度：中连续关键点趋势延续中再次放量突破整理区间，强度：中/弱反转关键点前高附近放量不突破，或跌破重要支撑，强度：强计算频率每日收盘后自动计算
STOCK-02 开仓检查
项目说明大盘条件大盘状态为底部区或震荡区关键点条件出现突破关键点或自然回撤关键点成交量条件量比>1.5板块条件板块同步走强（可选）风控条件未触发风控锁定，连续亏损<2次仓位条件个股总仓位<50%，单只<20%
STOCK-07 金字塔加仓建议
项目说明加仓前提当前持仓盈利加仓信号出现连续关键点加仓间隔每上涨5%可加仓一次加仓规模第一次50%，第二次30%，第三次20%止损调整加仓后整体止损上移至成本价
6.3 涉及表结构
（复用position_position和position_transaction，增加以下字段）
position_keypoint_signal
字段名类型说明idINT主键user_idINT用户IDsymbolVARCHAR(20)股票代码dateDATE信号日期keypoint_typeVARCHAR(30)关键点类型strengthVARCHAR(10)强度：强/中/弱priceDECIMAL(10,4)信号价格volume_ratioDECIMAL(10,4)量比statusVARCHAR(20)状态：pending/acted/expiredcreated_atDATETIME创建时间
--------------------------------------------------------------------------------
七、箱体分析模块
7.1 功能清单
功能编号功能名称功能描述输入输出BOX-01识别箱体自动识别个股箱体区间个股K线数据箱体上下沿BOX-02手动创建箱体用户手动创建箱体股票代码、上下沿箱体记录BOX-03更新箱体更新箱体确认次数箱体ID、当前价更新后箱体BOX-04判断箱体位置判断当前价格在箱体中的位置箱体、当前价上/中/下1/3区BOX-05获取箱体操作建议根据箱体位置和确认次数获取建议箱体信息、成交量买入/卖出/持有建议BOX-06箱体突破判断判断是否突破箱体箱体、当前价、成交量突破方向、有效性BOX-07箱体止损提醒判断是否跌破箱体下沿箱体、当前价止损提醒BOX-08箱体列表获取用户所有箱体用户ID箱体列表
7.2 功能细节
BOX-01 识别箱体
项目说明识别方法分析最近30-60天的高低点，聚类找出主要支撑和压力位箱体要求上下沿至少被触及2-3次，箱体高度>3%识别频率每日自动识别或用户手动触发输出信息上沿价格、下沿价格、箱体高度、确认次数
BOX-05 获取箱体操作建议
项目说明跌破下沿清仓，止损离场放量突破上沿有效突破，持有/加仓缩量突破上沿假突破，减仓下1/3区+确认3次买入下1/3区+确认2次可买入下1/3区+确认1次减仓/观望上1/3区减仓/止盈中1/3区持有观察
7.3 涉及表结构
box_boxrecord
字段名类型说明idINT主键user_idINT用户IDsymbolVARCHAR(20)股票代码nameVARCHAR(50)股票名称topDECIMAL(10,4)箱体上沿bottomDECIMAL(10,4)箱体下沿heightDECIMAL(10,4)箱体高度height_rateDECIMAL(10,4)箱体高度率(%)bottom_confirm_countINT底部确认次数top_confirm_countINT顶部确认次数statusVARCHAR(20)状态：active/broken_up/broken_downcreated_atDATETIME创建时间updated_atDATETIME更新时间
--------------------------------------------------------------------------------
八、做T管理模块
8.1 功能清单
功能编号功能名称功能描述输入输出DT-01做T开关控制根据大盘状态自动控制做T开关大盘状态做T是否允许DT-02记录做T记录做T交易买入价、卖出价、股票代码做T记录DT-03计算做T盈亏计算单次做T盈亏率买入价、卖出价盈亏率DT-04统计成功率统计近20次做T成功率用户ID成功率百分比DT-05检查暂停条件检查是否触发做T暂停连续失败次数、周成功率是否暂停DT-06做T提醒做T时弹出规则提醒操作类型提醒内容
8.2 功能细节
DT-01 做T开关控制
项目说明允许做T状态仅震荡区禁止做T状态底部区、上涨区、主升浪、陷阱区、下跌期开关方式系统自动控制，用户无法手动开启界面显示做T面板显示当前开关状态和原因
DT-04 统计成功率
项目说明统计周期近20次做T成功定义盈亏率 >= 0.5%显示方式百分比，红色(<60%)，绿色(>80%)更新频率每次新增做T记录后更新
DT-05 检查暂停条件
项目说明日内暂停连续失败2次，当天暂停周暂停一周成功率<60%，暂停一周恢复方式时间到期自动恢复，或用户确认后手动恢复
8.3 涉及表结构
daytrade_daytraderecord
字段名类型说明idINT主键user_idINT用户IDsymbolVARCHAR(20)股票代码buy_priceDECIMAL(10,4)买入价sell_priceDECIMAL(10,4)卖出价profit_rateDECIMAL(10,4)盈亏率(%)successBOOLEAN是否成功duration_minutesINT持仓时长(分钟)created_atDATETIME创建时间
daytrade_daytradestats
字段名类型说明idINT主键user_idINT用户IDdateDATE统计日期total_countINT总次数success_countINT成功次数success_rateDECIMAL(5,2)成功率(%)consecutive_failuresINT连续失败次数is_pausedBOOLEAN是否暂停pause_reasonVARCHAR(100)暂停原因pause_untilDATE暂停截止日期
--------------------------------------------------------------------------------
九、风险管理模块
9.1 功能清单
功能编号功能名称功能描述输入输出RISK-01计算单笔风险计算建议买入仓位总资金、止损幅度建议买入金额RISK-02检查单笔风险检查是否超风险限额买入金额、止损幅度是否超限RISK-03更新每日回撤更新账户每日回撤总市值变化日回撤、周回撤RISK-04检查回撤熔断检查是否触发回撤熔断日回撤、周回撤是否触发熔断RISK-05更新连续亏损更新连续亏损次数交易盈亏连续亏损次数RISK-06检查连续亏损保护检查是否触发保护连续亏损次数是否触发保护RISK-07重置风控重置风控状态无重置结果RISK-08获取风控状态获取当前风控状态用户ID风控状态信息
9.2 功能细节
RISK-01 计算单笔风险
项目说明计算公式建议买入金额 = 总资金 × 风险比例 / 止损幅度默认风险比例2%输出限制不超过单只个股仓位上限(20%)
RISK-04 检查回撤熔断
项目说明单日熔断日回撤 > -3%，建议非ETF仓位降至10%以下，休息3天周熔断周回撤 > -6%，强制风控，休息3个交易日熔断动作锁定交易按钮，弹出提醒，记录风控日志
RISK-06 检查连续亏损保护
项目说明触发条件连续亏损2次保护动作当日停止个股交易，弹出提醒重置条件次日自动重置
9.3 涉及表结构
risk_riskstatus
字段名类型说明idINT主键user_idINT用户IDdateDATE日期total_capitalDECIMAL(15,2)总资金total_valueDECIMAL(15,2)总市值daily_returnDECIMAL(10,4)当日回撤(%)weekly_returnDECIMAL(10,4)周回撤(%)consecutive_lossesINT连续亏损次数today_tradesINT今日交易次数risk_lockBOOLEAN风控锁定lock_reasonVARCHAR(200)锁定原因lock_untilDATE锁定截止日期created_atDATETIME创建时间
risk_risklog
字段名类型说明idINT主键user_idINT用户IDdateDATE日期risk_typeVARCHAR(30)风险类型trigger_valueDECIMAL(10,4)触发值actionVARCHAR(100)执行动作created_atDATETIME创建时间
--------------------------------------------------------------------------------
十、策略配置模块
10.1 功能清单
功能编号功能名称功能描述输入输出CFG-01获取策略配置获取用户策略配置用户ID配置参数CFG-02更新策略配置更新用户策略配置配置参数更新结果CFG-03重置默认配置重置为默认配置用户ID重置结果CFG-04导出配置导出配置为JSON用户IDJSON文件CFG-05导入配置从JSON导入配置JSON文件导入结果
10.2 功能细节
CFG-02 更新策略配置
参数名称默认值可调范围说明bottom_threshold-8-5 ~ -15底部区跌幅阈值(%)bottom_rsi3520 ~ 40底部区RSI阈值extreme_down_threshold-12-10 ~ -20极端超跌阈值(%)extreme_rsi2515 ~ 30极度超卖RSI阈值up_threshold53 ~ 10上涨区涨幅阈值(%)up_rsi7060 ~ 80上涨区RSI阈值stop_loss_rate53 ~ 10固定止损率(%)per_trade_risk21 ~ 3单笔风险限额(%)day_trade_target0.750.5 ~ 1做T目标(%)day_trade_stop0.50.3 ~ 1做T止损(%)single_stock_max2010 ~ 30单只个股最大仓位(%)time_stop_days105 ~ 20时间止损天数volume_breakout_ratio5030 ~ 100放量突破阈值(%)
10.3 涉及表结构
config_systemconfig
字段名类型说明idINT主键user_idINT用户IDconfig_keyVARCHAR(50)配置键config_valueVARCHAR(200)配置值descriptionVARCHAR(200)描述created_atDATETIME创建时间updated_atDATETIME更新时间
--------------------------------------------------------------------------------
十一、报表分析模块
11.1 功能清单
功能编号功能名称功能描述输入输出RPT-01交易统计统计期间交易次数、胜率日期范围统计报表RPT-02盈亏分析统计期间总盈亏、平均盈亏日期范围盈亏报表RPT-03月度报告生成月度交易报告年月月度报告RPT-04个股绩效统计各股票盈亏情况日期范围个股绩效表RPT-05策略绩效统计各策略类型盈亏日期范围策略绩效表RPT-06做T绩效统计做T盈亏和成功率日期范围做T绩效表RPT-07回撤分析统计期间最大回撤日期范围回撤曲线
11.2 功能细节
RPT-01 交易统计
项目说明统计指标总交易次数、盈利次数、亏损次数、胜率分组方式按日/周/月/年分组输出格式表格 + 图表
RPT-02 盈亏分析
项目说明统计指标总盈亏、平均盈亏、最大单笔盈利、最大单笔亏损、盈亏比输出格式表格 + 图表
11.3 涉及表结构
（复用已有表进行查询统计，无新增表）
--------------------------------------------------------------------------------
十二、表结构设计
12.1 表清单
序号表名说明1users_user用户表2users_userprofile用户配置表3market_marketdata市场数据表4market_technicalindicators技术指标表5strategy_marketstate市场状态表6strategy_eventcalendar事件日历表7position_position持仓表8position_transaction交易记录表9position_keypoint_signal关键点信号表10box_boxrecord箱体记录表11daytrade_daytraderecord做T记录表12daytrade_daytradestats做T统计表13risk_riskstatus风控状态表14risk_risklog风控日志表15config_systemconfig系统配置表16sync_synclog同步日志表
12.2 表结构详细定义
12.2.1 users_user（用户表）
字段名类型允许空默认值说明idINT否AUTO主键usernameVARCHAR(150)否-用户名，唯一passwordVARCHAR(128)否-加密密码emailVARCHAR(254)否-邮箱is_activeBOOLEAN否TRUE是否激活last_loginDATETIME是NULL最后登录时间created_atDATETIME否CURRENT_TIME创建时间
12.2.2 users_userprofile（用户配置表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-关联用户IDtotal_capitalDECIMAL(15,2)否100000.00总资金tushare_tokenVARCHAR(100)是NULLTushare TokenthemeVARCHAR(20)否light主题：light/darkcreated_atDATETIME否CURRENT_TIME创建时间updated_atDATETIME否CURRENT_TIME更新时间
12.2.3 market_marketdata（市场数据表）
字段名类型允许空默认值说明idINT否AUTO主键dateDATE否-交易日期index_codeVARCHAR(20)否-指数代码openDECIMAL(10,4)是NULL开盘价highDECIMAL(10,4)是NULL最高价lowDECIMAL(10,4)是NULL最低价closeDECIMAL(10,4)否-收盘价volumeBIGINT是NULL成交量amountBIGINT是NULL成交额created_atDATETIME否CURRENT_TIME创建时间
12.2.4 market_technicalindicators（技术指标表）
字段名类型允许空默认值说明idINT否AUTO主键market_data_idINT否-关联市场数据IDchange_20dDECIMAL(10,4)是NULL20日涨跌幅(%)rsi_14DECIMAL(10,4)是NULL14日RSIma_5DECIMAL(10,4)是NULL5日均线ma_20DECIMAL(10,4)是NULL20日均线ma_60DECIMAL(10,4)是NULL60日均线obvBIGINT是NULLOBV值obv_trendVARCHAR(20)是NULLOBV趋势volume_ratioDECIMAL(10,4)是NULL量比divergenceVARCHAR(20)是无背离背离状态macd_difDECIMAL(10,4)是NULLMACD DIFmacd_deaDECIMAL(10,4)是NULLMACD DEAmacd_barDECIMAL(10,4)是NULLMACD柱created_atDATETIME否CURRENT_TIME创建时间
12.2.5 strategy_marketstate（市场状态表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDdateDATE否-日期tech_stateVARCHAR(20)是NULL技术状态major_trendVARCHAR(20)是NULL主要趋势cycle_stateVARCHAR(20)是NULL大周期状态event_correctionVARCHAR(20)是NULL事件修正final_stateVARCHAR(20)是NULL最终状态max_positionINT是NULL建议仓位上限(%)etf_actionVARCHAR(50)是NULLETF建议动作individual_actionVARCHAR(50)是NULL个股建议动作exit_levelINT是NULL离场级别exit_reasonVARCHAR(100)是NULL离场原因created_atDATETIME否CURRENT_TIME创建时间
12.2.6 strategy_eventcalendar（事件日历表）
字段名类型允许空默认值说明idINT否AUTO主键event_nameVARCHAR(100)否-事件名称event_typeVARCHAR(20)否-类型start_dateDATE否-开始日期end_dateDATE否-结束日期correction_valueDECIMAL(5,2)否0修正值yearINT否-年份descriptionVARCHAR(200)是NULL描述created_atDATETIME否CURRENT_TIME创建时间
12.2.7 position_position（持仓表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDsymbolVARCHAR(20)否-股票代码nameVARCHAR(50)否-股票名称typeVARCHAR(20)否individual类型：etf/individuallogicVARCHAR(20)否trend逻辑：trend/box/short_termbuy_dateDATE否-买入日期buy_priceDECIMAL(10,4)否-买入价quantityINT否-数量stop_lossDECIMAL(10,4)是NULL止损价target_priceDECIMAL(10,4)是NULL目标价statusVARCHAR(20)否holding状态created_atDATETIME否CURRENT_TIME创建时间updated_atDATETIME否CURRENT_TIME更新时间
12.2.8 position_transaction（交易记录表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDposition_idINT是NULL关联持仓IDdateDATE否-交易日期directionVARCHAR(10)否-方向：buy/sellpriceDECIMAL(10,4)否-成交价quantityINT否-数量amountDECIMAL(15,2)否-金额feeDECIMAL(10,4)否0手续费logic_typeVARCHAR(50)是NULL逻辑类型created_atDATETIME否CURRENT_TIME创建时间
12.2.9 position_keypoint_signal（关键点信号表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDsymbolVARCHAR(20)否-股票代码dateDATE否-信号日期keypoint_typeVARCHAR(30)否-关键点类型strengthVARCHAR(10)否-强度priceDECIMAL(10,4)否-信号价格volume_ratioDECIMAL(10,4)是NULL量比statusVARCHAR(20)否pending状态created_atDATETIME否CURRENT_TIME创建时间
12.2.10 box_boxrecord（箱体记录表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDsymbolVARCHAR(20)否-股票代码nameVARCHAR(50)是NULL股票名称topDECIMAL(10,4)否-箱体上沿bottomDECIMAL(10,4)否-箱体下沿heightDECIMAL(10,4)是NULL箱体高度height_rateDECIMAL(10,4)是NULL箱体高度率(%)bottom_confirm_countINT否1底部确认次数top_confirm_countINT否1顶部确认次数statusVARCHAR(20)否active状态created_atDATETIME否CURRENT_TIME创建时间updated_atDATETIME否CURRENT_TIME更新时间
12.2.11 daytrade_daytraderecord（做T记录表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDsymbolVARCHAR(20)否-股票代码buy_priceDECIMAL(10,4)否-买入价sell_priceDECIMAL(10,4)否-卖出价profit_rateDECIMAL(10,4)是NULL盈亏率(%)successBOOLEAN否FALSE是否成功duration_minutesINT是NULL持仓时长(分钟)created_atDATETIME否CURRENT_TIME创建时间
12.2.12 daytrade_daytradestats（做T统计表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDdateDATE否-统计日期total_countINT否0总次数success_countINT否0成功次数success_rateDECIMAL(5,2)否0成功率(%)consecutive_failuresINT否0连续失败次数is_pausedBOOLEAN否FALSE是否暂停pause_reasonVARCHAR(100)是NULL暂停原因pause_untilDATE是NULL暂停截止日期created_atDATETIME否CURRENT_TIME创建时间
12.2.13 risk_riskstatus（风控状态表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDdateDATE否-日期total_capitalDECIMAL(15,2)否-总资金total_valueDECIMAL(15,2)是NULL总市值daily_returnDECIMAL(10,4)是NULL当日回撤(%)weekly_returnDECIMAL(10,4)是NULL周回撤(%)consecutive_lossesINT否0连续亏损次数today_tradesINT否0今日交易次数risk_lockBOOLEAN否FALSE风控锁定lock_reasonVARCHAR(200)是NULL锁定原因lock_untilDATE是NULL锁定截止日期created_atDATETIME否CURRENT_TIME创建时间
12.2.14 risk_risklog（风控日志表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDdateDATE否-日期risk_typeVARCHAR(30)否-风险类型trigger_valueDECIMAL(10,4)是NULL触发值actionVARCHAR(100)否-执行动作created_atDATETIME否CURRENT_TIME创建时间
12.2.15 config_systemconfig（系统配置表）
字段名类型允许空默认值说明idINT否AUTO主键user_idINT否-用户IDconfig_keyVARCHAR(50)否-配置键config_valueVARCHAR(200)否-配置值descriptionVARCHAR(200)是NULL描述created_atDATETIME否CURRENT_TIME创建时间updated_atDATETIME否CURRENT_TIME更新时间
12.2.16 sync_synclog（同步日志表）
字段名类型允许空默认值说明idINT否AUTO主键sync_typeVARCHAR(20)否-同步类型target_codeVARCHAR(20)否-目标代码start_dateDATE否-开始日期end_dateDATE否-结束日期synced_countINT否0同步记录数statusVARCHAR(20)否-状态error_messageTEXT是NULL错误信息created_atDATETIME否CURRENT_TIME创建时间