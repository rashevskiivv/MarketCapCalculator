from tkinter import *
import os
import time

from utils_ui import Table

companies = []
results_file = 'results.csv'
symbols_file = 'symbols.csv'

# Filters
target_pe = 30
sign_pe = '>'
target_ps = 10
sign_ps = '>'
target_pb = 3
sign_pb = '>'
target_eps = 1
sign_eps = '<'
target_roe = 0.1
sign_roe = '<'
target_roa = 0.05
sign_roa = '<'
target_market_cap = 1_000_000_000
sign_market_cap = '<'
target_ebitda = 1_000_000_000 #@todo check
sign_ebitda = '<'
target_total_debt = 1_000_000_000 #@todo check
sign_total_debt = '>'
target_rps = 1
sign_rps = '>'

# Colors for print
color_green_to_print = '\033[1;92m'
color_red_to_print = '\033[1;91m'

# For ui
placeholder = 'Input a number'
less_text = 'less'
more_than_text = 'more than'
global_x = 0
global_width = []


def on_focus_in(entry):
    if entry.cget('state') == 'disabled':
        entry.configure(state='normal')
        entry.delete(0, 'end')


def on_focus_out(entry, placeholder_inner):
    if entry.get() == "":
        entry.insert(0, placeholder_inner)
        entry.configure(state='disabled')


def create_label(master, text, row, column):
    label = Label(master=master, text=text)
    label.grid(row=row, column=column)


def create_radio_buttons(master, row, column):
    var = StringVar()
    less_rb = Radiobutton(master=master, text=less_text, value=less_text, variable=var)
    less_rb.select()
    less_rb.grid(row=row, column=column)
    more_rb = Radiobutton(master=master, text=more_than_text, value=more_than_text, variable=var)
    more_rb.grid(row=row, column=column + 1)
    return var


def create_entry(master, row, column):
    entry = Entry(master=master)
    entry.grid(row=row, column=column)
    entry.insert(0, placeholder)
    entry.configure(state='disabled')
    entry.bind('<Button-1>', lambda x_: on_focus_in(entry))
    entry.bind('<FocusOut>', lambda x_: on_focus_out(entry, placeholder))
    return entry


def create_filter(master, filter_text):
    global counter_row, counter_column
    create_label(master, filter_text, counter_row, counter_column)
    counter_column += 1

    rb = create_radio_buttons(master, counter_row, counter_column)
    counter_column += 2

    e = create_entry(master, counter_row, counter_column)
    counter_row += 1
    counter_column = 0
    return rb, e


def get_current_time_milliseconds():
    return round(time.time() * 1000)


def read_csv_and_fill_data():
    index = 0
    with open(symbols_file, 'r') as f:
        for line in f:
            if line.__contains__('Symbol') or line.strip().__eq__(''):
                continue
            companies.append([])
            _, symbol = list(line.split(','))
            symbol = symbol.replace('\n', '')
            companies[index].append(symbol)
            index += 1


def read_csv_results():
    index = 0
    with open(results_file, 'r') as f:
        for line in f:
            companies.append([])
            symbol, sector, industry, price, nums = list(line.split(','))
            companies[index].append(symbol)
            companies[index].append(sector)
            companies[index].append(industry)
            if line.__contains__('Symbol'):
                companies[index].append(price)
                companies[index].append(nums)
            else:
                companies[index].append(float(price))
                companies[index].append(int(nums))
            index += 1


def prepare_output_file():
    with open(results_file, 'w') as f:
        f.write('Symbol,Sector,Industry,Current/last price in USD,Number of stocks\n')


def append_number_of_stocks_output():
    from shutil import copy as sh_copy
    input_f = 'buf.csv'
    sh_copy(results_file, input_f)
    with open(results_file, 'w') as out_file:
        with open(input_f, 'r') as in_file:
            j = 0
            for line in in_file:
                if line.__contains__('Symbol'):
                    out_file.write(line)
                    continue
                s = line.rstrip('\n') + ',' + str(companies[j][4]) + '\n'
                out_file.write(s)
                j += 1
    os.remove('buf.csv')


def append_company_output(company):
    with open(results_file, 'a') as f:
        f.write(f'{company[0]},{company[1]},{company[2]},{company[3]}\n')


def write_full_output():
    with open(results_file, 'w') as f:
        f.write('Symbol,Sector,Industry,Current/last price in USD,Number of stocks\n')
        # Sector include industry
        for j in range(len(companies)):
            f.write(f'{companies[j][0]},{companies[j][1]},{companies[j][2]},'
                    f'{companies[j][3]},{companies[j][4]}\n')


def sort_by_symbol():
    companies.sort(key=lambda x: x[0], reverse=True)


def sort_by_sector():
    companies.sort(key=lambda x: x[1], reverse=False)


def sort_by_industry():
    companies.sort(key=lambda x: x[2], reverse=False)


def get_data_yf():
    import requests
    import json
    url = "https://yh-finance.p.rapidapi.com/stock/v2/get-summary"
    headers = {
        "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
        "X-RapidAPI-Key": "c14ba60263msh1d75ac31f7bbeeap1f679ejsn684e4f6dccb8"
    }
    # "X-RapidAPI-Key": "f761bc90aemsh14894d87cb4757ap1851d5jsn8e91db991e16" = 0
    # https://smailpro.com/advanced
    j = 0
    while j < len(companies):
        querystring = {"symbol": f'{companies[j][0]}'}
        symbol = requests.request("GET", url, headers=headers, params=querystring)
        # symbol = """{"defaultKeyStatistics":{"annualHoldingsTurnover":{},"enterpriseToRevenue":{"raw":0.396,"fmt":"0.40"},"beta3Year":{},"profitMargins":{"raw":-0.04146,"fmt":"-4.15%"},"enterpriseToEbitda":{"raw":575.203,"fmt":"575.20"},"52WeekChange":{"raw":-0.6780045,"fmt":"-67.80%"},"morningStarRiskRating":{},"forwardEps":{"raw":-0.16,"fmt":"-0.16"},"revenueQuarterlyGrowth":{},"sharesOutstanding":{"raw":397008000,"fmt":"397.01M","longFmt":"397,008,000"},"fundInceptionDate":{},"annualReportExpenseRatio":{},"totalAssets":{},"bookValue":{"raw":1.615,"fmt":"1.62"},"sharesShort":{"raw":18090207,"fmt":"18.09M","longFmt":"18,090,207"},"sharesPercentSharesOut":{"raw":0.0456,"fmt":"4.56%"},"fundFamily":null,"lastFiscalYearEnd":{"raw":1640908800,"fmt":"2021-12-31"},"heldPercentInstitutions":{"raw":0.34666002,"fmt":"34.67%"},"netIncomeToCommon":{"raw":-22208000,"fmt":"-22.21M","longFmt":"-22,208,000"},"trailingEps":{"raw":-0.056,"fmt":"-0.0560"},"lastDividendValue":{},"SandP52WeekChange":{"raw":-0.070451856,"fmt":"-7.05%"},"priceToBook":{"raw":0.87925696,"fmt":"0.88"},"heldPercentInsiders":{"raw":0.012940001,"fmt":"1.29%"},"nextFiscalYearEnd":{"raw":1703980800,"fmt":"2023-12-31"},"yield":{},"mostRecentQuarter":{"raw":1648684800,"fmt":"2022-03-31"},"shortRatio":{"raw":7.87,"fmt":"7.87"},"sharesShortPreviousMonthDate":{"raw":1648684800,"fmt":"2022-03-31"},"floatShares":{"raw":345305216,"fmt":"345.31M","longFmt":"345,305,216"},"beta":{"raw":2.083482,"fmt":"2.08"},"enterpriseValue":{"raw":212250080,"fmt":"212.25M","longFmt":"212,250,080"},"priceHint":{"raw":4,"fmt":"4","longFmt":"4"},"threeYearAverageReturn":{},"lastSplitDate":{"raw":1200614400,"fmt":"2008-01-18"},"lastSplitFactor":"1:10","legalType":null,"lastDividendDate":{},"morningStarOverallRating":{},"earningsQuarterlyGrowth":{},"priceToSalesTrailing12Months":{},"dateShortInterest":{"raw":1651190400,"fmt":"2022-04-29"},"pegRatio":{"raw":-0.17,"fmt":"-0.17"},"ytdReturn":{},"forwardPE":{"raw":-8.875,"fmt":"-8.88"},"maxAge":1,"lastCapGain":{},"shortPercentOfFloat":{},"sharesShortPriorMonth":{"raw":16488879,"fmt":"16.49M","longFmt":"16,488,879"},"impliedSharesOutstanding":{"raw":0,"fmt":null,"longFmt":"0"},"category":null,"fiveYearAverageReturn":{}},"details":{},"summaryProfile":{"zip":"2","sector":"Healthcare","fullTimeEmployees":560,"longBusinessSummary":"Amarin Corporation plc, a pharmaceutical company, engages in the development and commercialization of therapeutics for the treatment of cardiovascular diseases in the United States, Germany, Canada, Lebanon, and the United Arab Emirates. Its lead product is VASCEPA, a prescription-only omega-3 fatty acid product, used as an adjunct to diet for reducing triglyceride levels in adult patients with severe hypertriglyceridemia. The company sells its products principally to wholesalers and specialty pharmacy providers. It has a collaboration with Mochida Pharmaceutical Co., Ltd. to develop and commercialize drug products and indications based on the active pharmaceutical ingredient in Vascepa, the omega-3 acid, and eicosapentaenoic acid. The company was formerly known as Ethical Holdings plc and changed its name to Amarin Corporation plc in 1999. Amarin Corporation plc was incorporated in 1989 and is headquartered in Dublin, Ireland.","city":"Dublin","phone":"353 1 669 9020","country":"Ireland","companyOfficers":[],"website":"https://www.amarincorp.com","maxAge":86400,"address1":"Grand Canal Docklands","industry":"Biotechnology","address2":"Block C 77 Sir John Rogerson's Quay"},"recommendationTrend":{"trend":[{"period":"0m","strongBuy":2,"buy":3,"hold":0,"sell":0,"strongSell":0},{"period":"-1m","strongBuy":1,"buy":4,"hold":2,"sell":1,"strongSell":0},{"period":"-2m","strongBuy":1,"buy":5,"hold":2,"sell":1,"strongSell":0},{"period":"-3m","strongBuy":2,"buy":3,"hold":0,"sell":0,"strongSell":0}],"maxAge":86400},"financialsTemplate":{"code":"N","maxAge":1},"majorDirectHolders":{"holders":[],"maxAge":1},"earnings":{"maxAge":86400,"earningsChart":{"quarterly":[{"date":"2Q2021","actual":{"raw":0.02,"fmt":"0.02"},"estimate":{"raw":-0.03,"fmt":"-0.03"}},{"date":"3Q2021","actual":{"raw":-0.03,"fmt":"-0.03"},"estimate":{"raw":-0.04,"fmt":"-0.04"}},{"date":"4Q2021","actual":{"raw":0.04,"fmt":"0.04"},"estimate":{"raw":-0.02,"fmt":"-0.02"}},{"date":"1Q2022","actual":{"raw":-0.08,"fmt":"-0.08"},"estimate":{"raw":-0.02,"fmt":"-0.02"}}],"currentQuarterEstimate":{"raw":-0.05,"fmt":"-0.05"},"currentQuarterEstimateDate":"2Q","currentQuarterEstimateYear":2022,"earningsDate":[{"raw":1651647601,"fmt":"2022-05-04"}]},"financialsChart":{"yearly":[{"date":2018,"revenue":{"raw":229214000,"fmt":"229.21M","longFmt":"229,214,000"},"earnings":{"raw":-116445000,"fmt":"-116.44M","longFmt":"-116,445,000"}},{"date":2019,"revenue":{"raw":429755000,"fmt":"429.75M","longFmt":"429,755,000"},"earnings":{"raw":-22645000,"fmt":"-22.64M","longFmt":"-22,645,000"}},{"date":2020,"revenue":{"raw":614060000,"fmt":"614.06M","longFmt":"614,060,000"},"earnings":{"raw":-18000000,"fmt":"-18M","longFmt":"-18,000,000"}},{"date":2021,"revenue":{"raw":583187000,"fmt":"583.19M","longFmt":"583,187,000"},"earnings":{"raw":7729000,"fmt":"7.73M","longFmt":"7,729,000"}}],"quarterly":[{"date":"2Q2021","revenue":{"raw":154488000,"fmt":"154.49M","longFmt":"154,488,000"},"earnings":{"raw":7808000,"fmt":"7.81M","longFmt":"7,808,000"}},{"date":"3Q2021","revenue":{"raw":142038000,"fmt":"142.04M","longFmt":"142,038,000"},"earnings":{"raw":-13151000,"fmt":"-13.15M","longFmt":"-13,151,000"}},{"date":"4Q2021","revenue":{"raw":144491000,"fmt":"144.49M","longFmt":"144,491,000"},"earnings":{"raw":14698000,"fmt":"14.7M","longFmt":"14,698,000"}},{"date":"1Q2022","revenue":{"raw":94630000,"fmt":"94.63M","longFmt":"94,630,000"},"earnings":{"raw":-31563000,"fmt":"-31.56M","longFmt":"-31,563,000"}}]},"financialCurrency":"USD"},"price":{"quoteSourceName":"Nasdaq Real Time Price","regularMarketOpen":{"raw":1.49,"fmt":"1.4900"},"averageDailyVolume3Month":{"raw":4026573,"fmt":"4.03M","longFmt":"4,026,573"},"exchange":"NGM","regularMarketTime":1653076804,"volume24Hr":{},"regularMarketDayHigh":{"raw":1.495,"fmt":"1.4950"},"shortName":"Amarin Corporation plc","averageDailyVolume10Day":{"raw":5081650,"fmt":"5.08M","longFmt":"5,081,650"},"longName":"Amarin Corporation plc","regularMarketChange":{"raw":-0.0200001,"fmt":"-0.0200"},"currencySymbol":"$","regularMarketPreviousClose":{"raw":1.44,"fmt":"1.4400"},"postMarketTime":1653090193,"preMarketPrice":{"raw":1.47,"fmt":"1.4700"},"preMarketTime":1653304510,"exchangeDataDelayedBy":0,"toCurrency":null,"postMarketChange":{"raw":0.0700001,"fmt":"0.07"},"postMarketPrice":{"raw":1.49,"fmt":"1.4900"},"exchangeName":"NasdaqGM","preMarketChange":{"raw":0.05000007,"fmt":"0.05"},"circulatingSupply":{},"regularMarketDayLow":{"raw":1.35,"fmt":"1.3500"},"priceHint":{"raw":4,"fmt":"4","longFmt":"4"},"currency":"USD","regularMarketPrice":{"raw":1.42,"fmt":"1.4200"},"regularMarketVolume":{"raw":2039439,"fmt":"2.04M","longFmt":"2,039,439.00"},"lastMarket":null,"regularMarketSource":"FREE_REALTIME","openInterest":{},"marketState":"PRE","underlyingSymbol":null,"marketCap":{"raw":563751360,"fmt":"563.75M","longFmt":"563,751,360.00"},"quoteType":"EQUITY","preMarketChangePercent":{"raw":0.03521132,"fmt":"3.52%"},"volumeAllCurrencies":{},"postMarketSource":"FREE_REALTIME","strikePrice":{},"symbol":"AMRN","postMarketChangePercent":{"raw":0.0492958,"fmt":"4.93%"},"preMarketSource":"FREE_REALTIME","maxAge":1,"fromCurrency":null,"regularMarketChangePercent":{"raw":-0.013888958,"fmt":"-1.39%"}},"fundOwnership":{"maxAge":1,"ownershipList":[{"maxAge":1,"reportDate":{"raw":1643587200,"fmt":"2022-01-31"},"organization":"Legg Mason Glb Asset Mgt Tr-Clearbridge Small Cap Fd","pctHeld":{"raw":0.0085,"fmt":"0.85%"},"position":{"raw":3365059,"fmt":"3.37M","longFmt":"3,365,059"},"value":{"raw":12181513,"fmt":"12.18M","longFmt":"12,181,513"}},{"maxAge":1,"reportDate":{"raw":1640908800,"fmt":"2021-12-31"},"organization":"Value Line Capital Appreciation Fund","pctHeld":{"raw":0.0043,"fmt":"0.43%"},"position":{"raw":1700000,"fmt":"1.7M","longFmt":"1,700,000"},"value":{"raw":5729000,"fmt":"5.73M","longFmt":"5,729,000"}},{"maxAge":1,"reportDate":{"raw":1640908800,"fmt":"2021-12-31"},"organization":"Value Line Larger Companies Focused Fund","pctHeld":{"raw":0.003,"fmt":"0.30%"},"position":{"raw":1200000,"fmt":"1.2M","longFmt":"1,200,000"},"value":{"raw":4044000,"fmt":"4.04M","longFmt":"4,044,000"}},{"maxAge":1,"reportDate":{"raw":1640908800,"fmt":"2021-12-31"},"organization":"Guardian VP Tr-Guardian Small Cap Core VIP Fd","pctHeld":{"raw":0.0021,"fmt":"0.21%"},"position":{"raw":825686,"fmt":"825.69k","longFmt":"825,686"},"value":{"raw":2782561,"fmt":"2.78M","longFmt":"2,782,561"}},{"maxAge":1,"reportDate":{"raw":1640908800,"fmt":"2021-12-31"},"organization":"Columbia Fds Var Ser Tr II-Columbia Var Port-Overseas Core Fd","pctHeld":{"raw":0.0013,"fmt":"0.13%"},"position":{"raw":517951,"fmt":"517.95k","longFmt":"517,951"},"value":{"raw":1745494,"fmt":"1.75M","longFmt":"1,745,494"}},{"maxAge":1,"reportDate":{"raw":1646006400,"fmt":"2022-02-28"},"organization":"VanEck ETF Trust-VanEck Pharmaceutical ETF","pctHeld":{"raw":0.0011999999,"fmt":"0.12%"},"position":{"raw":482391,"fmt":"482.39k","longFmt":"482,391"},"value":{"raw":1596714,"fmt":"1.6M","longFmt":"1,596,714"}},{"maxAge":1,"reportDate":{"raw":1640908800,"fmt":"2021-12-31"},"organization":"Legg Mason Clearbridge Small Cap Value Fd","pctHeld":{"raw":0.00090000004,"fmt":"0.09%"},"position":{"raw":372770,"fmt":"372.77k","longFmt":"372,770"},"value":{"raw":1256234,"fmt":"1.26M","longFmt":"1,256,234"}},{"maxAge":1,"reportDate":{"raw":1646006400,"fmt":"2022-02-28"},"organization":"Columbia Fds Ser Tr-Columbia Overseas Value Fd","pctHeld":{"raw":0.0008,"fmt":"0.08%"},"position":{"raw":311700,"fmt":"311.7k","longFmt":"311,700"},"value":{"raw":1031727,"fmt":"1.03M","longFmt":"1,031,727"}},{"maxAge":1,"reportDate":{"raw":1646006400,"fmt":"2022-02-28"},"organization":"Fidelity NASDAQ Composite Index Fund","pctHeld":{"raw":0.0005,"fmt":"0.05%"},"position":{"raw":214385,"fmt":"214.38k","longFmt":"214,385"},"value":{"raw":709614,"fmt":"709.61k","longFmt":"709,614"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"Monetta Fund, Inc.","pctHeld":{"raw":0.0005,"fmt":"0.05%"},"position":{"raw":200000,"fmt":"200k","longFmt":"200,000"},"value":{"raw":658000,"fmt":"658k","longFmt":"658,000"}}]},"insiderTransactions":{"transactions":[{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1646006400,"fmt":"2022-02-28"},"filerRelation":"Officer","shares":{"raw":16333,"fmt":"16.33k","longFmt":"16,333"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1646006400,"fmt":"2022-02-28"},"filerRelation":"Chief Financial Officer","shares":{"raw":16333,"fmt":"16.33k","longFmt":"16,333"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1643587200,"fmt":"2022-01-31"},"filerRelation":"Officer","shares":{"raw":12733,"fmt":"12.73k","longFmt":"12,733"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1643587200,"fmt":"2022-01-31"},"filerRelation":"Chief Financial Officer","shares":{"raw":12733,"fmt":"12.73k","longFmt":"12,733"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1643587200,"fmt":"2022-01-31"},"filerRelation":"Officer","shares":{"raw":12733,"fmt":"12.73k","longFmt":"12,733"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1640908800,"fmt":"2021-12-31"},"filerRelation":"Officer","shares":{"raw":47767,"fmt":"47.77k","longFmt":"47,767"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1640908800,"fmt":"2021-12-31"},"filerRelation":"Chief Financial Officer","shares":{"raw":47767,"fmt":"47.77k","longFmt":"47,767"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1640908800,"fmt":"2021-12-31"},"filerRelation":"Officer","shares":{"raw":47767,"fmt":"47.77k","longFmt":"47,767"},"filerUrl":"","maxAge":1},{"filerName":"MIKHAIL KARIM","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1640908800,"fmt":"2021-12-31"},"filerRelation":"Chief Executive Officer","shares":{"raw":11367,"fmt":"11.37k","longFmt":"11,367"},"filerUrl":"","maxAge":1},{"filerName":"ZAKRZEWSKI JOSEPH S","transactionText":"Purchase at price 3.15 - 3.27 per share.","moneyText":"","ownership":"D","startDate":{"raw":1639526400,"fmt":"2021-12-15"},"value":{"raw":38999,"fmt":"39k","longFmt":"38,999"},"filerRelation":"Director","shares":{"raw":12000,"fmt":"12k","longFmt":"12,000"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1630368000,"fmt":"2021-08-31"},"filerRelation":"Officer","shares":{"raw":6108,"fmt":"6.11k","longFmt":"6,108"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1630368000,"fmt":"2021-08-31"},"filerRelation":"Chief Financial Officer","shares":{"raw":6108,"fmt":"6.11k","longFmt":"6,108"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1630368000,"fmt":"2021-08-31"},"filerRelation":"Officer","shares":{"raw":6108,"fmt":"6.11k","longFmt":"6,108"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"Sale at price 5.25 per share.","moneyText":"","ownership":"D","startDate":{"raw":1628726400,"fmt":"2021-08-12"},"value":{"raw":630240,"fmt":"630.24k","longFmt":"630,240"},"filerRelation":"Chief Financial Officer","shares":{"raw":120000,"fmt":"120k","longFmt":"120,000"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"Conversion of Exercise of derivative security at price 2.19 - 2.95 per share.","moneyText":"","ownership":"D","startDate":{"raw":1628726400,"fmt":"2021-08-12"},"value":{"raw":281800,"fmt":"281.8k","longFmt":"281,800"},"filerRelation":"Chief Financial Officer","shares":{"raw":120000,"fmt":"120k","longFmt":"120,000"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1627603200,"fmt":"2021-07-30"},"filerRelation":"Chief Executive Officer","shares":{"raw":26944,"fmt":"26.94k","longFmt":"26,944"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1627603200,"fmt":"2021-07-30"},"filerRelation":"General Counsel","shares":{"raw":7220,"fmt":"7.22k","longFmt":"7,220"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1627603200,"fmt":"2021-07-30"},"filerRelation":"Officer","shares":{"raw":6108,"fmt":"6.11k","longFmt":"6,108"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1627603200,"fmt":"2021-07-30"},"filerRelation":"Chief Financial Officer","shares":{"raw":6108,"fmt":"6.11k","longFmt":"6,108"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1627603200,"fmt":"2021-07-30"},"filerRelation":"Officer","shares":{"raw":6108,"fmt":"6.11k","longFmt":"6,108"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1625011200,"fmt":"2021-06-30"},"filerRelation":"Chief Executive Officer","shares":{"raw":26944,"fmt":"26.94k","longFmt":"26,944"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1625011200,"fmt":"2021-06-30"},"filerRelation":"General Counsel","shares":{"raw":7220,"fmt":"7.22k","longFmt":"7,220"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1625011200,"fmt":"2021-06-30"},"filerRelation":"Officer","shares":{"raw":6108,"fmt":"6.11k","longFmt":"6,108"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1625011200,"fmt":"2021-06-30"},"filerRelation":"Chief Financial Officer","shares":{"raw":6108,"fmt":"6.11k","longFmt":"6,108"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1625011200,"fmt":"2021-06-30"},"filerRelation":"Officer","shares":{"raw":6108,"fmt":"6.11k","longFmt":"6,108"},"filerUrl":"","maxAge":1},{"filerName":"STACK DAVID M","transactionText":"Purchase at price 4.54 - 4.62 per share.","moneyText":"","ownership":"I","startDate":{"raw":1622764800,"fmt":"2021-06-04"},"value":{"raw":68465,"fmt":"68.47k","longFmt":"68,465"},"filerRelation":"Director","shares":{"raw":15000,"fmt":"15k","longFmt":"15,000"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1622160000,"fmt":"2021-05-28"},"filerRelation":"Chief Executive Officer","shares":{"raw":26944,"fmt":"26.94k","longFmt":"26,944"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1622160000,"fmt":"2021-05-28"},"filerRelation":"General Counsel","shares":{"raw":7220,"fmt":"7.22k","longFmt":"7,220"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1622160000,"fmt":"2021-05-28"},"filerRelation":"Officer","shares":{"raw":6112,"fmt":"6.11k","longFmt":"6,112"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1622160000,"fmt":"2021-05-28"},"filerRelation":"Chief Financial Officer","shares":{"raw":6112,"fmt":"6.11k","longFmt":"6,112"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1622160000,"fmt":"2021-05-28"},"filerRelation":"Officer","shares":{"raw":6112,"fmt":"6.11k","longFmt":"6,112"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1619740800,"fmt":"2021-04-30"},"filerRelation":"Chief Executive Officer","shares":{"raw":26944,"fmt":"26.94k","longFmt":"26,944"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1619740800,"fmt":"2021-04-30"},"filerRelation":"General Counsel","shares":{"raw":7220,"fmt":"7.22k","longFmt":"7,220"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1619740800,"fmt":"2021-04-30"},"filerRelation":"Officer","shares":{"raw":6112,"fmt":"6.11k","longFmt":"6,112"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1619740800,"fmt":"2021-04-30"},"filerRelation":"Chief Financial Officer","shares":{"raw":6112,"fmt":"6.11k","longFmt":"6,112"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1619740800,"fmt":"2021-04-30"},"filerRelation":"Officer","shares":{"raw":32112,"fmt":"32.11k","longFmt":"32,112"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1617148800,"fmt":"2021-03-31"},"filerRelation":"Chief Executive Officer","shares":{"raw":26944,"fmt":"26.94k","longFmt":"26,944"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1617148800,"fmt":"2021-03-31"},"filerRelation":"General Counsel","shares":{"raw":7220,"fmt":"7.22k","longFmt":"7,220"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1617148800,"fmt":"2021-03-31"},"filerRelation":"Officer","shares":{"raw":6112,"fmt":"6.11k","longFmt":"6,112"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1617148800,"fmt":"2021-03-31"},"filerRelation":"Chief Financial Officer","shares":{"raw":6112,"fmt":"6.11k","longFmt":"6,112"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1617148800,"fmt":"2021-03-31"},"filerRelation":"Officer","shares":{"raw":6112,"fmt":"6.11k","longFmt":"6,112"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1614297600,"fmt":"2021-02-26"},"filerRelation":"Chief Executive Officer","shares":{"raw":477007,"fmt":"477.01k","longFmt":"477,007"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1614297600,"fmt":"2021-02-26"},"filerRelation":"General Counsel","shares":{"raw":128286,"fmt":"128.29k","longFmt":"128,286"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1614297600,"fmt":"2021-02-26"},"filerRelation":"Officer","shares":{"raw":111060,"fmt":"111.06k","longFmt":"111,060"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1614297600,"fmt":"2021-02-26"},"filerRelation":"Chief Financial Officer","shares":{"raw":111060,"fmt":"111.06k","longFmt":"111,060"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1614297600,"fmt":"2021-02-26"},"filerRelation":"Officer","shares":{"raw":111060,"fmt":"111.06k","longFmt":"111,060"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"Sale at price 8.03 - 8.06 per share.","moneyText":"","ownership":"D","startDate":{"raw":1612137600,"fmt":"2021-02-01"},"value":{"raw":1754134,"fmt":"1.75M","longFmt":"1,754,134"},"filerRelation":"Officer","shares":{"raw":217728,"fmt":"217.73k","longFmt":"217,728"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"Conversion of Exercise of derivative security at price 2.50 - 2.95 per share.","moneyText":"","ownership":"D","startDate":{"raw":1612137600,"fmt":"2021-02-01"},"value":{"raw":485882,"fmt":"485.88k","longFmt":"485,882"},"filerRelation":"Officer","shares":{"raw":192358,"fmt":"192.36k","longFmt":"192,358"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1611878400,"fmt":"2021-01-29"},"filerRelation":"Chief Executive Officer","shares":{"raw":209171,"fmt":"209.17k","longFmt":"209,171"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1611878400,"fmt":"2021-01-29"},"filerRelation":"General Counsel","shares":{"raw":42345,"fmt":"42.34k","longFmt":"42,345"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"Conversion of Exercise of derivative security at price 1.02 - 3.80 per share.","moneyText":"","ownership":"D","startDate":{"raw":1611878400,"fmt":"2021-01-29"},"value":{"raw":764566,"fmt":"764.57k","longFmt":"764,566"},"filerRelation":"Officer","shares":{"raw":320026,"fmt":"320.03k","longFmt":"320,026"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1611878400,"fmt":"2021-01-29"},"filerRelation":"Chief Financial Officer","shares":{"raw":41789,"fmt":"41.79k","longFmt":"41,789"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1611878400,"fmt":"2021-01-29"},"filerRelation":"Officer","shares":{"raw":15789,"fmt":"15.79k","longFmt":"15,789"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"Sale at price 8.01 per share.","moneyText":"","ownership":"D","startDate":{"raw":1611705600,"fmt":"2021-01-27"},"value":{"raw":3378131,"fmt":"3.38M","longFmt":"3,378,131"},"filerRelation":"Officer","shares":{"raw":421629,"fmt":"421.63k","longFmt":"421,629"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1609372800,"fmt":"2020-12-31"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1609372800,"fmt":"2020-12-31"},"filerRelation":"General Counsel","shares":{"raw":3612,"fmt":"3.61k","longFmt":"3,612"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1609372800,"fmt":"2020-12-31"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1606694400,"fmt":"2020-11-30"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"STACK DAVID M","transactionText":"Purchase at price 4.86 per share.","moneyText":"","ownership":"I","startDate":{"raw":1606694400,"fmt":"2020-11-30"},"value":{"raw":121518,"fmt":"121.52k","longFmt":"121,518"},"filerRelation":"Director","shares":{"raw":25000,"fmt":"25k","longFmt":"25,000"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1606694400,"fmt":"2020-11-30"},"filerRelation":"General Counsel","shares":{"raw":3612,"fmt":"3.61k","longFmt":"3,612"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1606694400,"fmt":"2020-11-30"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1606694400,"fmt":"2020-11-30"},"filerRelation":"Chief Financial Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1606694400,"fmt":"2020-11-30"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"Sale at price 4.07 - 4.13 per share.","moneyText":"","ownership":"D","startDate":{"raw":1605052800,"fmt":"2020-11-11"},"value":{"raw":2317158,"fmt":"2.32M","longFmt":"2,317,158"},"filerRelation":"Chief Executive Officer","shares":{"raw":567405,"fmt":"567.4k","longFmt":"567,405"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"Conversion of Exercise of derivative security at price 3.40 per share.","moneyText":"","ownership":"D","startDate":{"raw":1604966400,"fmt":"2020-11-10"},"value":{"raw":2550000,"fmt":"2.55M","longFmt":"2,550,000"},"filerRelation":"Chief Executive Officer","shares":{"raw":750000,"fmt":"750k","longFmt":"750,000"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1604016000,"fmt":"2020-10-30"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1604016000,"fmt":"2020-10-30"},"filerRelation":"General Counsel","shares":{"raw":3612,"fmt":"3.61k","longFmt":"3,612"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1604016000,"fmt":"2020-10-30"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1604016000,"fmt":"2020-10-30"},"filerRelation":"Chief Financial Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1604016000,"fmt":"2020-10-30"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"ZAKRZEWSKI JOSEPH S","transactionText":"Conversion of Exercise of derivative security at price 3.40 per share.","moneyText":"","ownership":"D","startDate":{"raw":1603238400,"fmt":"2020-10-21"},"value":{"raw":340000,"fmt":"340k","longFmt":"340,000"},"filerRelation":"Director","shares":{"raw":100000,"fmt":"100k","longFmt":"100,000"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1601424000,"fmt":"2020-09-30"},"filerRelation":"Chief Executive Officer","shares":{"raw":13474,"fmt":"13.47k","longFmt":"13,474"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1601424000,"fmt":"2020-09-30"},"filerRelation":"General Counsel","shares":{"raw":3612,"fmt":"3.61k","longFmt":"3,612"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1601424000,"fmt":"2020-09-30"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1601424000,"fmt":"2020-09-30"},"filerRelation":"Chief Financial Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1601424000,"fmt":"2020-09-30"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1598832000,"fmt":"2020-08-31"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1598832000,"fmt":"2020-08-31"},"filerRelation":"General Counsel","shares":{"raw":3610,"fmt":"3.61k","longFmt":"3,610"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1598832000,"fmt":"2020-08-31"},"filerRelation":"Officer","shares":{"raw":3054,"fmt":"3.05k","longFmt":"3,054"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1598832000,"fmt":"2020-08-31"},"filerRelation":"Chief Financial Officer","shares":{"raw":3054,"fmt":"3.05k","longFmt":"3,054"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1598832000,"fmt":"2020-08-31"},"filerRelation":"Officer","shares":{"raw":3054,"fmt":"3.05k","longFmt":"3,054"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1596153600,"fmt":"2020-07-31"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1596153600,"fmt":"2020-07-31"},"filerRelation":"General Counsel","shares":{"raw":3610,"fmt":"3.61k","longFmt":"3,610"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1596153600,"fmt":"2020-07-31"},"filerRelation":"Officer","shares":{"raw":3054,"fmt":"3.05k","longFmt":"3,054"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1596153600,"fmt":"2020-07-31"},"filerRelation":"Chief Financial Officer","shares":{"raw":3054,"fmt":"3.05k","longFmt":"3,054"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1596153600,"fmt":"2020-07-31"},"filerRelation":"Officer","shares":{"raw":3054,"fmt":"3.05k","longFmt":"3,054"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1593475200,"fmt":"2020-06-30"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1593475200,"fmt":"2020-06-30"},"filerRelation":"General Counsel","shares":{"raw":3610,"fmt":"3.61k","longFmt":"3,610"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1593475200,"fmt":"2020-06-30"},"filerRelation":"Officer","shares":{"raw":3054,"fmt":"3.05k","longFmt":"3,054"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1593475200,"fmt":"2020-06-30"},"filerRelation":"Chief Financial Officer","shares":{"raw":3054,"fmt":"3.05k","longFmt":"3,054"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1593475200,"fmt":"2020-06-30"},"filerRelation":"Officer","shares":{"raw":3054,"fmt":"3.05k","longFmt":"3,054"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1590710400,"fmt":"2020-05-29"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1590710400,"fmt":"2020-05-29"},"filerRelation":"General Counsel","shares":{"raw":3610,"fmt":"3.61k","longFmt":"3,610"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1590710400,"fmt":"2020-05-29"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1590710400,"fmt":"2020-05-29"},"filerRelation":"Chief Financial Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1590710400,"fmt":"2020-05-29"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1588291200,"fmt":"2020-05-01"},"filerRelation":"Officer","shares":{"raw":29056,"fmt":"29.06k","longFmt":"29,056"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1588204800,"fmt":"2020-04-30"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1588204800,"fmt":"2020-04-30"},"filerRelation":"General Counsel","shares":{"raw":3610,"fmt":"3.61k","longFmt":"3,610"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1588204800,"fmt":"2020-04-30"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1588204800,"fmt":"2020-04-30"},"filerRelation":"Chief Financial Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1585612800,"fmt":"2020-03-31"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1585612800,"fmt":"2020-03-31"},"filerRelation":"General Counsel","shares":{"raw":3612,"fmt":"3.61k","longFmt":"3,612"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1585612800,"fmt":"2020-03-31"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1585612800,"fmt":"2020-03-31"},"filerRelation":"Chief Financial Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1585612800,"fmt":"2020-03-31"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"Sale at price 15.99 per share.","moneyText":"","ownership":"D","startDate":{"raw":1583280000,"fmt":"2020-03-04"},"value":{"raw":3198700,"fmt":"3.2M","longFmt":"3,198,700"},"filerRelation":"Chief Executive Officer","shares":{"raw":200000,"fmt":"200k","longFmt":"200,000"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582848000,"fmt":"2020-02-28"},"filerRelation":"Chief Executive Officer","shares":{"raw":13472,"fmt":"13.47k","longFmt":"13,472"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582848000,"fmt":"2020-02-28"},"filerRelation":"General Counsel","shares":{"raw":3612,"fmt":"3.61k","longFmt":"3,612"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582848000,"fmt":"2020-02-28"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582848000,"fmt":"2020-02-28"},"filerRelation":"Chief Financial Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582848000,"fmt":"2020-02-28"},"filerRelation":"Officer","shares":{"raw":3056,"fmt":"3.06k","longFmt":"3,056"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582588800,"fmt":"2020-02-25"},"filerRelation":"Chief Executive Officer","shares":{"raw":229030,"fmt":"229.03k","longFmt":"229,030"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582588800,"fmt":"2020-02-25"},"filerRelation":"General Counsel","shares":{"raw":61394,"fmt":"61.39k","longFmt":"61,394"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582588800,"fmt":"2020-02-25"},"filerRelation":"Officer","shares":{"raw":51948,"fmt":"51.95k","longFmt":"51,948"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582588800,"fmt":"2020-02-25"},"filerRelation":"Chief Financial Officer","shares":{"raw":51948,"fmt":"51.95k","longFmt":"51,948"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1582588800,"fmt":"2020-02-25"},"filerRelation":"Officer","shares":{"raw":51948,"fmt":"51.95k","longFmt":"51,948"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1580428800,"fmt":"2020-01-31"},"filerRelation":"Chief Executive Officer","shares":{"raw":315367,"fmt":"315.37k","longFmt":"315,367"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1580428800,"fmt":"2020-01-31"},"filerRelation":"General Counsel","shares":{"raw":74734,"fmt":"74.73k","longFmt":"74,734"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1580428800,"fmt":"2020-01-31"},"filerRelation":"Officer","shares":{"raw":67734,"fmt":"67.73k","longFmt":"67,734"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1580428800,"fmt":"2020-01-31"},"filerRelation":"Chief Financial Officer","shares":{"raw":67734,"fmt":"67.73k","longFmt":"67,734"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"","moneyText":"","ownership":"D","startDate":{"raw":1580428800,"fmt":"2020-01-31"},"filerRelation":"Officer","shares":{"raw":41734,"fmt":"41.73k","longFmt":"41,734"},"filerUrl":"","maxAge":1},{"filerName":"ZAKRZEWSKI JOSEPH S","transactionText":"Sale at price 20.94 per share.","moneyText":"","ownership":"D","startDate":{"raw":1578009600,"fmt":"2020-01-03"},"value":{"raw":6282870,"fmt":"6.28M","longFmt":"6,282,870"},"filerRelation":"Director","shares":{"raw":300000,"fmt":"300k","longFmt":"300,000"},"filerUrl":"","maxAge":1},{"filerName":"ZAKRZEWSKI JOSEPH S","transactionText":"Conversion of Exercise of derivative security at price 3.40 per share.","moneyText":"","ownership":"D","startDate":{"raw":1578009600,"fmt":"2020-01-03"},"value":{"raw":1020000,"fmt":"1.02M","longFmt":"1,020,000"},"filerRelation":"Director","shares":{"raw":300000,"fmt":"300k","longFmt":"300,000"},"filerUrl":"","maxAge":1},{"filerName":"ZAKRZEWSKI JOSEPH S","transactionText":"Sale at price 25.83 per share.","moneyText":"","ownership":"D","startDate":{"raw":1576454400,"fmt":"2019-12-16"},"value":{"raw":2583380,"fmt":"2.58M","longFmt":"2,583,380"},"filerRelation":"Director","shares":{"raw":100000,"fmt":"100k","longFmt":"100,000"},"filerUrl":"","maxAge":1},{"filerName":"ZAKRZEWSKI JOSEPH S","transactionText":"Conversion of Exercise of derivative security at price 9.00 per share.","moneyText":"","ownership":"D","startDate":{"raw":1576454400,"fmt":"2019-12-16"},"value":{"raw":900000,"fmt":"900k","longFmt":"900,000"},"filerRelation":"Director","shares":{"raw":100000,"fmt":"100k","longFmt":"100,000"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"Sale at price 23.05 - 25.66 per share.","moneyText":"","ownership":"D","startDate":{"raw":1576454400,"fmt":"2019-12-16"},"value":{"raw":584012,"fmt":"584.01k","longFmt":"584,012"},"filerRelation":"Chief Financial Officer","shares":{"raw":25000,"fmt":"25k","longFmt":"25,000"},"filerUrl":"","maxAge":1},{"filerName":"KALB MICHAEL WAYNE","transactionText":"Conversion of Exercise of derivative security at price 2.19 per share.","moneyText":"","ownership":"D","startDate":{"raw":1576454400,"fmt":"2019-12-16"},"value":{"raw":54750,"fmt":"54.75k","longFmt":"54,750"},"filerRelation":"Chief Financial Officer","shares":{"raw":25000,"fmt":"25k","longFmt":"25,000"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"Sale at price 25.46 per share.","moneyText":"","ownership":"D","startDate":{"raw":1576454400,"fmt":"2019-12-16"},"value":{"raw":1101364,"fmt":"1.1M","longFmt":"1,101,364"},"filerRelation":"Officer","shares":{"raw":43253,"fmt":"43.25k","longFmt":"43,253"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"Conversion of Exercise of derivative security at price 12.60 per share.","moneyText":"","ownership":"D","startDate":{"raw":1576454400,"fmt":"2019-12-16"},"value":{"raw":544988,"fmt":"544.99k","longFmt":"544,988"},"filerRelation":"Officer","shares":{"raw":43253,"fmt":"43.25k","longFmt":"43,253"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"Sale at price 22.65 per share.","moneyText":"","ownership":"D","startDate":{"raw":1574121600,"fmt":"2019-11-19"},"value":{"raw":6217371,"fmt":"6.22M","longFmt":"6,217,371"},"filerRelation":"Chief Executive Officer","shares":{"raw":274454,"fmt":"274.45k","longFmt":"274,454"},"filerUrl":"","maxAge":1},{"filerName":"EKMAN LARS G","transactionText":"Sale at price 19.35 per share.","moneyText":"","ownership":"D","startDate":{"raw":1573516800,"fmt":"2019-11-12"},"value":{"raw":746759,"fmt":"746.76k","longFmt":"746,759"},"filerRelation":"Director","shares":{"raw":38600,"fmt":"38.6k","longFmt":"38,600"},"filerUrl":"","maxAge":1},{"filerName":"EKMAN LARS G","transactionText":"Conversion of Exercise of derivative security at price 14.40 per share.","moneyText":"","ownership":"D","startDate":{"raw":1573516800,"fmt":"2019-11-12"},"value":{"raw":555840,"fmt":"555.84k","longFmt":"555,840"},"filerRelation":"Director","shares":{"raw":38600,"fmt":"38.6k","longFmt":"38,600"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"Sale at price 17.05 - 17.88 per share.","moneyText":"","ownership":"D","startDate":{"raw":1573430400,"fmt":"2019-11-11"},"value":{"raw":8143452,"fmt":"8.14M","longFmt":"8,143,452"},"filerRelation":"Chief Executive Officer","shares":{"raw":475546,"fmt":"475.55k","longFmt":"475,546"},"filerUrl":"","maxAge":1},{"filerName":"EKMAN LARS G","transactionText":"Sale at price 18.00 per share.","moneyText":"","ownership":"D","startDate":{"raw":1572912000,"fmt":"2019-11-05"},"value":{"raw":115230,"fmt":"115.23k","longFmt":"115,230"},"filerRelation":"Director","shares":{"raw":6400,"fmt":"6.4k","longFmt":"6,400"},"filerUrl":"","maxAge":1},{"filerName":"EKMAN LARS G","transactionText":"Conversion of Exercise of derivative security at price 14.40 per share.","moneyText":"","ownership":"D","startDate":{"raw":1572912000,"fmt":"2019-11-05"},"value":{"raw":92160,"fmt":"92.16k","longFmt":"92,160"},"filerRelation":"Director","shares":{"raw":6400,"fmt":"6.4k","longFmt":"6,400"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"Conversion of Exercise of derivative security at price 2.50 per share.","moneyText":"","ownership":"D","startDate":{"raw":1572220800,"fmt":"2019-10-28"},"value":{"raw":29002,"fmt":"29k","longFmt":"29,002"},"filerRelation":"Chief Executive Officer","shares":{"raw":11601,"fmt":"11.6k","longFmt":"11,601"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"Stock Award(Grant) at price 0.00 per share.","moneyText":"","ownership":"D","startDate":{"raw":1570406400,"fmt":"2019-10-07"},"value":{"raw":0,"fmt":null,"longFmt":"0"},"filerRelation":"Chief Executive Officer","shares":{"raw":1265250,"fmt":"1.27M","longFmt":"1,265,250"},"filerUrl":"","maxAge":1},{"filerName":"KENNEDY JOSEPH T","transactionText":"Stock Award(Grant) at price 0.00 per share.","moneyText":"","ownership":"D","startDate":{"raw":1570406400,"fmt":"2019-10-07"},"value":{"raw":0,"fmt":null,"longFmt":"0"},"filerRelation":"General Counsel","shares":{"raw":199500,"fmt":"199.5k","longFmt":"199,500"},"filerUrl":"","maxAge":1},{"filerName":"KETCHUM STEVEN B","transactionText":"Stock Award(Grant) at price 0.00 per share.","moneyText":"","ownership":"D","startDate":{"raw":1570406400,"fmt":"2019-10-07"},"value":{"raw":0,"fmt":null,"longFmt":"0"},"filerRelation":"Officer","shares":{"raw":199500,"fmt":"199.5k","longFmt":"199,500"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"Stock Award(Grant) at price 0.00 per share.","moneyText":"","ownership":"D","startDate":{"raw":1570406400,"fmt":"2019-10-07"},"value":{"raw":0,"fmt":null,"longFmt":"0"},"filerRelation":"Officer","shares":{"raw":199500,"fmt":"199.5k","longFmt":"199,500"},"filerUrl":"","maxAge":1},{"filerName":"EKMAN LARS G","transactionText":"Sale at price 15.01 per share.","moneyText":"","ownership":"D","startDate":{"raw":1567468800,"fmt":"2019-09-03"},"value":{"raw":1365722,"fmt":"1.37M","longFmt":"1,365,722"},"filerRelation":"Director","shares":{"raw":91016,"fmt":"91.02k","longFmt":"91,016"},"filerUrl":"","maxAge":1},{"filerName":"EKMAN LARS G","transactionText":"Conversion of Exercise of derivative security at price 3.06 - 5.58 per share.","moneyText":"","ownership":"D","startDate":{"raw":1567468800,"fmt":"2019-09-03"},"value":{"raw":320280,"fmt":"320.28k","longFmt":"320,280"},"filerRelation":"Director","shares":{"raw":91016,"fmt":"91.02k","longFmt":"91,016"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"Conversion of Exercise of derivative security at price 1.02 - 2.50 per share.","moneyText":"","ownership":"D","startDate":{"raw":1566345600,"fmt":"2019-08-21"},"value":{"raw":300010,"fmt":"300.01k","longFmt":"300,010"},"filerRelation":"Chief Executive Officer","shares":{"raw":191997,"fmt":"192k","longFmt":"191,997"},"filerUrl":"","maxAge":1},{"filerName":"THERO JOHN F","transactionText":"Conversion of Exercise of derivative security at price 1.02 - 2.50 per share.","moneyText":"","ownership":"D","startDate":{"raw":1566345600,"fmt":"2019-08-21"},"value":{"raw":271008,"fmt":"271.01k","longFmt":"271,008"},"filerRelation":"Chief Executive Officer","shares":{"raw":180396,"fmt":"180.4k","longFmt":"180,396"},"filerUrl":"","maxAge":1},{"filerName":"STACK DAVID M","transactionText":"Sale at price 22.28 per share.","moneyText":"","ownership":"I","startDate":{"raw":1562803200,"fmt":"2019-07-11"},"value":{"raw":1158354,"fmt":"1.16M","longFmt":"1,158,354"},"filerRelation":"Director","shares":{"raw":51991,"fmt":"51.99k","longFmt":"51,991"},"filerUrl":"","maxAge":1},{"filerName":"STACK DAVID M","transactionText":"Conversion of Exercise of derivative security at price 2.19 - 2.50 per share.","moneyText":"","ownership":"I","startDate":{"raw":1562803200,"fmt":"2019-07-11"},"value":{"raw":121035,"fmt":"121.03k","longFmt":"121,035"},"filerRelation":"Director","shares":{"raw":51991,"fmt":"51.99k","longFmt":"51,991"},"filerUrl":"","maxAge":1},{"filerName":"ZAKRZEWSKI JOSEPH S","transactionText":"Sale at price 23.82 per share.","moneyText":"","ownership":"D","startDate":{"raw":1562284800,"fmt":"2019-07-05"},"value":{"raw":2381580,"fmt":"2.38M","longFmt":"2,381,580"},"filerRelation":"Director","shares":{"raw":100000,"fmt":"100k","longFmt":"100,000"},"filerUrl":"","maxAge":1},{"filerName":"ZAKRZEWSKI JOSEPH S","transactionText":"Conversion of Exercise of derivative security at price 9.00 per share.","moneyText":"","ownership":"D","startDate":{"raw":1562284800,"fmt":"2019-07-05"},"value":{"raw":900000,"fmt":"900k","longFmt":"900,000"},"filerRelation":"Director","shares":{"raw":100000,"fmt":"100k","longFmt":"100,000"},"filerUrl":"","maxAge":1},{"filerName":"BERG AARON D.","transactionText":"Sale at price 20.46 - 22.64 per share.","moneyText":"","ownership":"D","startDate":{"raw":1562112000,"fmt":"2019-07-03"},"value":{"raw":2104378,"fmt":"2.1M","longFmt":"2,104,378"},"filerRelation":"Officer","shares":{"raw":98814,"fmt":"98.81k","longFmt":"98,814"},"filerUrl":"","maxAge":1}],"maxAge":1},"insiderHolders":{"holders":[{"maxAge":1,"name":"BERG AARON D.","relation":"Officer","url":"","transactionDescription":"Conversion of Exercise of derivative security","latestTransDate":{"raw":1643587200,"fmt":"2022-01-31"},"positionDirect":{"raw":375751,"fmt":"375.75k","longFmt":"375,751"},"positionDirectDate":{"raw":1643587200,"fmt":"2022-01-31"}},{"maxAge":1,"name":"EKMAN LARS G","relation":"Director","url":"","transactionDescription":"Sale","latestTransDate":{"raw":1573516800,"fmt":"2019-11-12"},"positionDirectDate":{"raw":1573516800,"fmt":"2019-11-12"}},{"maxAge":1,"name":"KALB MICHAEL WAYNE","relation":"Chief Financial Officer","url":"","transactionDescription":"Conversion of Exercise of derivative security","latestTransDate":{"raw":1646006400,"fmt":"2022-02-28"},"positionDirect":{"raw":250747,"fmt":"250.75k","longFmt":"250,747"},"positionDirectDate":{"raw":1646006400,"fmt":"2022-02-28"}},{"maxAge":1,"name":"KENNEDY JOSEPH T","relation":"General Counsel","url":"","transactionDescription":"Conversion of Exercise of derivative security","latestTransDate":{"raw":1627603200,"fmt":"2021-07-30"},"positionDirect":{"raw":317860,"fmt":"317.86k","longFmt":"317,860"},"positionDirectDate":{"raw":1627603200,"fmt":"2021-07-30"}},{"maxAge":1,"name":"KETCHUM STEVEN B","relation":"Officer","url":"","transactionDescription":"Conversion of Exercise of derivative security","latestTransDate":{"raw":1646006400,"fmt":"2022-02-28"},"positionDirect":{"raw":496912,"fmt":"496.91k","longFmt":"496,912"},"positionDirectDate":{"raw":1646006400,"fmt":"2022-02-28"}},{"maxAge":1,"name":"MIKHAIL KARIM","relation":"Chief Executive Officer","url":"","transactionDescription":"Conversion of Exercise of derivative security","latestTransDate":{"raw":1640908800,"fmt":"2021-12-31"},"positionDirect":{"raw":31031,"fmt":"31.03k","longFmt":"31,031"},"positionDirectDate":{"raw":1640908800,"fmt":"2021-12-31"}},{"maxAge":1,"name":"STACK DAVID M","relation":"Director","url":"","transactionDescription":"Purchase","latestTransDate":{"raw":1622764800,"fmt":"2021-06-04"},"positionIndirect":{"raw":40000,"fmt":"40k","longFmt":"40,000"},"positionIndirectDate":{"raw":1622764800,"fmt":"2021-06-04"}},{"maxAge":1,"name":"THERO JOHN F","relation":"Chief Executive Officer","url":"","transactionDescription":"Conversion of Exercise of derivative security","latestTransDate":{"raw":1627603200,"fmt":"2021-07-30"},"positionDirect":{"raw":3252750,"fmt":"3.25M","longFmt":"3,252,750"},"positionDirectDate":{"raw":1627603200,"fmt":"2021-07-30"}},{"maxAge":1,"name":"VAN HEEK G JAN","relation":"Director","url":"","transactionDescription":"Sale","latestTransDate":{"raw":1550793600,"fmt":"2019-02-22"},"positionDirect":{"raw":14168,"fmt":"14.17k","longFmt":"14,168"},"positionDirectDate":{"raw":1550793600,"fmt":"2019-02-22"}},{"maxAge":1,"name":"ZAKRZEWSKI JOSEPH S","relation":"Director","url":"","transactionDescription":"Purchase","latestTransDate":{"raw":1639526400,"fmt":"2021-12-15"},"positionDirect":{"raw":196547,"fmt":"196.55k","longFmt":"196,547"},"positionDirectDate":{"raw":1639526400,"fmt":"2021-12-15"}}],"maxAge":1},"netSharePurchaseActivity":{"period":"6m","netPercentInsiderShares":{"raw":0.049000002,"fmt":"4.90%"},"netInfoCount":{"raw":10,"fmt":"10","longFmt":"10"},"totalInsiderShares":{"raw":5134739,"fmt":"5.13M","longFmt":"5,134,739"},"buyInfoShares":{"raw":237533,"fmt":"237.53k","longFmt":"237,533"},"buyPercentInsiderShares":{"raw":0.049000002,"fmt":"4.90%"},"sellInfoCount":{"raw":0,"fmt":null,"longFmt":"0"},"maxAge":1,"buyInfoCount":{"raw":10,"fmt":"10","longFmt":"10"},"netInfoShares":{"raw":237533,"fmt":"237.53k","longFmt":"237,533"}},"majorHoldersBreakdown":{"maxAge":1,"insidersPercentHeld":{"raw":0.012940001,"fmt":"1.29%"},"institutionsPercentHeld":{"raw":0.34666002,"fmt":"34.67%"},"institutionsFloatPercentHeld":{"raw":0.35121,"fmt":"35.12%"},"institutionsCount":{"raw":266,"fmt":"266","longFmt":"266"}},"financialData":{"ebitdaMargins":{"raw":0.00068999996,"fmt":"0.07%"},"profitMargins":{"raw":-0.04146,"fmt":"-4.15%"},"grossMargins":{"raw":0.78486,"fmt":"78.49%"},"operatingCashflow":{"raw":-146680000,"fmt":"-146.68M","longFmt":"-146,680,000"},"revenueGrowth":{"raw":-0.334,"fmt":"-33.40%"},"operatingMargins":{"raw":-0.0051499996,"fmt":"-0.51%"},"ebitda":{"raw":369000,"fmt":"369k","longFmt":"369,000"},"targetLowPrice":{"raw":1.5,"fmt":"1.50"},"recommendationKey":"hold","grossProfits":{"raw":461860000,"fmt":"461.86M","longFmt":"461,860,000"},"freeCashflow":{"raw":11573250,"fmt":"11.57M","longFmt":"11,573,250"},"targetMedianPrice":{"raw":3,"fmt":"3.00"},"currentPrice":{"raw":1.42,"fmt":"1.42"},"earningsGrowth":{},"currentRatio":{"raw":2.57,"fmt":"2.57"},"returnOnAssets":{"raw":-0.0017499999,"fmt":"-0.17%"},"numberOfAnalystOpinions":{"raw":7,"fmt":"7","longFmt":"7"},"targetMeanPrice":{"raw":3.61,"fmt":"3.61"},"debtToEquity":{"raw":1.768,"fmt":"1.77"},"returnOnEquity":{"raw":-0.03482,"fmt":"-3.48%"},"targetHighPrice":{"raw":9,"fmt":"9.00"},"totalCash":{"raw":362556992,"fmt":"362.56M","longFmt":"362,556,992"},"totalDebt":{"raw":11335000,"fmt":"11.34M","longFmt":"11,335,000"},"totalRevenue":{"raw":535647008,"fmt":"535.65M","longFmt":"535,647,008"},"totalCashPerShare":{"raw":0.914,"fmt":"0.91"},"financialCurrency":"USD","maxAge":86400,"revenuePerShare":{"raw":1.35,"fmt":"1.35"},"quickRatio":{"raw":1.573,"fmt":"1.57"},"recommendationMean":{"raw":2.9,"fmt":"2.90"}},"quoteType":{"exchange":"NGM","shortName":"Amarin Corporation plc","longName":"Amarin Corporation plc","exchangeTimezoneName":"America/New_York","exchangeTimezoneShortName":"EDT","isEsgPopulated":false,"gmtOffSetMilliseconds":"-14400000","quoteType":"EQUITY","symbol":"AMRN","messageBoardId":"finmb_407863","market":"us_market"},"institutionOwnership":{"maxAge":1,"ownershipList":[{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"Sarissa Capital Management, LP","pctHeld":{"raw":0.060500003,"fmt":"6.05%"},"position":{"raw":24000000,"fmt":"24M","longFmt":"24,000,000"},"value":{"raw":78960000,"fmt":"78.96M","longFmt":"78,960,000"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"Baker Brothers Advisors, LLC","pctHeld":{"raw":0.053400002,"fmt":"5.34%"},"position":{"raw":21169805,"fmt":"21.17M","longFmt":"21,169,805"},"value":{"raw":69648658,"fmt":"69.65M","longFmt":"69,648,658"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"Eversept Partners, LP","pctHeld":{"raw":0.0226,"fmt":"2.26%"},"position":{"raw":8980145,"fmt":"8.98M","longFmt":"8,980,145"},"value":{"raw":29544677,"fmt":"29.54M","longFmt":"29,544,677"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"SCP Investment, LP","pctHeld":{"raw":0.017,"fmt":"1.70%"},"position":{"raw":6750000,"fmt":"6.75M","longFmt":"6,750,000"},"value":{"raw":22207500,"fmt":"22.21M","longFmt":"22,207,500"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"Avoro Capital Advisors LLC","pctHeld":{"raw":0.0150999995,"fmt":"1.51%"},"position":{"raw":6000000,"fmt":"6M","longFmt":"6,000,000"},"value":{"raw":19740000,"fmt":"19.74M","longFmt":"19,740,000"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"Stonepine Capital Management, LLC","pctHeld":{"raw":0.0124,"fmt":"1.24%"},"position":{"raw":4912714,"fmt":"4.91M","longFmt":"4,912,714"},"value":{"raw":16162829,"fmt":"16.16M","longFmt":"16,162,829"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"Millennium Management LLC","pctHeld":{"raw":0.0123000005,"fmt":"1.23%"},"position":{"raw":4885384,"fmt":"4.89M","longFmt":"4,885,384"},"value":{"raw":16072913,"fmt":"16.07M","longFmt":"16,072,913"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"ClearBridge Investments, LLC","pctHeld":{"raw":0.0121,"fmt":"1.21%"},"position":{"raw":4789575,"fmt":"4.79M","longFmt":"4,789,575"},"value":{"raw":15757701,"fmt":"15.76M","longFmt":"15,757,701"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"Morgan Stanley","pctHeld":{"raw":0.0117,"fmt":"1.17%"},"position":{"raw":4638240,"fmt":"4.64M","longFmt":"4,638,240"},"value":{"raw":15259809,"fmt":"15.26M","longFmt":"15,259,809"}},{"maxAge":1,"reportDate":{"raw":1648684800,"fmt":"2022-03-31"},"organization":"Rock Springs Capital Management, LP","pctHeld":{"raw":0.0111,"fmt":"1.11%"},"position":{"raw":4419700,"fmt":"4.42M","longFmt":"4,419,700"},"value":{"raw":14540813,"fmt":"14.54M","longFmt":"14,540,813"}}]},"calendarEvents":{"maxAge":1,"earnings":{"earningsDate":[{"raw":1651647601,"fmt":"2022-05-04"}],"earningsAverage":{"raw":-0.05,"fmt":"-0.05"},"earningsLow":{"raw":-0.1,"fmt":"-0.10"},"earningsHigh":{"raw":-0.03,"fmt":"-0.03"},"revenueAverage":{"raw":95000000,"fmt":"95M","longFmt":"95,000,000"},"revenueLow":{"raw":67000000,"fmt":"67M","longFmt":"67,000,000"},"revenueHigh":{"raw":113400000,"fmt":"113.4M","longFmt":"113,400,000"}},"exDividendDate":{},"dividendDate":{}},"summaryDetail":{"previousClose":{"raw":1.44,"fmt":"1.4400"},"regularMarketOpen":{"raw":1.49,"fmt":"1.4900"},"twoHundredDayAverage":{"raw":3.8275,"fmt":"3.8275"},"trailingAnnualDividendYield":{"raw":0,"fmt":"0.00%"},"payoutRatio":{"raw":0,"fmt":"0.00%"},"volume24Hr":{},"regularMarketDayHigh":{"raw":1.495,"fmt":"1.4950"},"navPrice":{},"averageDailyVolume10Day":{"raw":5081650,"fmt":"5.08M","longFmt":"5,081,650"},"totalAssets":{},"regularMarketPreviousClose":{"raw":1.44,"fmt":"1.4400"},"fiftyDayAverage":{"raw":2.7088,"fmt":"2.7088"},"trailingAnnualDividendRate":{"raw":0,"fmt":"0.00"},"open":{"raw":1.49,"fmt":"1.4900"},"toCurrency":null,"averageVolume10days":{"raw":5081650,"fmt":"5.08M","longFmt":"5,081,650"},"expireDate":{},"yield":{},"algorithm":null,"dividendRate":{},"exDividendDate":{},"beta":{"raw":2.083482,"fmt":"2.08"},"circulatingSupply":{},"startDate":{},"regularMarketDayLow":{"raw":1.35,"fmt":"1.3500"},"priceHint":{"raw":4,"fmt":"4","longFmt":"4"},"currency":"USD","regularMarketVolume":{"raw":2039439,"fmt":"2.04M","longFmt":"2,039,439"},"lastMarket":null,"maxSupply":{},"openInterest":{},"marketCap":{"raw":563751360,"fmt":"563.75M","longFmt":"563,751,360"},"volumeAllCurrencies":{},"strikePrice":{},"averageVolume":{"raw":4026573,"fmt":"4.03M","longFmt":"4,026,573"},"priceToSalesTrailing12Months":{"raw":1.0524681,"fmt":"1.05"},"dayLow":{"raw":1.35,"fmt":"1.3500"},"ask":{"raw":0,"fmt":"0.0000"},"ytdReturn":{},"askSize":{"raw":21500,"fmt":"21.5k","longFmt":"21,500"},"volume":{"raw":2039439,"fmt":"2.04M","longFmt":"2,039,439"},"fiftyTwoWeekHigh":{"raw":5.97,"fmt":"5.9700"},"forwardPE":{"raw":-8.875,"fmt":"-8.88"},"maxAge":1,"fromCurrency":null,"fiveYearAvgDividendYield":{},"fiftyTwoWeekLow":{"raw":1.11,"fmt":"1.1100"},"bid":{"raw":1.42,"fmt":"1.4200"},"tradeable":false,"dividendYield":{},"bidSize":{"raw":21500,"fmt":"21.5k","longFmt":"21,500"},"dayHigh":{"raw":1.495,"fmt":"1.4950"}},"symbol":"AMRN","esgScores":{},"upgradeDowngradeHistory":{"history":[{"epochGradeDate":1651827113,"firm":"JP Morgan","toGrade":"Underweight","fromGrade":"Neutral","action":"down"},{"epochGradeDate":1651747244,"firm":"HC Wainwright & Co.","toGrade":"Neutral","fromGrade":"Buy","action":"down"},{"epochGradeDate":1651745119,"firm":"SVB Leerink","toGrade":"Market Perform","fromGrade":"Outperform","action":"down"},{"epochGradeDate":1645006655,"firm":"SVB Leerink","toGrade":"Outperform","fromGrade":"","action":"main"},{"epochGradeDate":1643639948,"firm":"SVB Leerink","toGrade":"Outperform","fromGrade":"","action":"main"},{"epochGradeDate":1631184703,"firm":"SVB Leerink","toGrade":"Outperform","fromGrade":"","action":"init"},{"epochGradeDate":1620816711,"firm":"Goldman Sachs","toGrade":"Sell","fromGrade":"Neutral","action":"down"},{"epochGradeDate":1612177851,"firm":"SVB Leerink","toGrade":"Outperform","fromGrade":"","action":"main"},{"epochGradeDate":1601287572,"firm":"SVB Leerink","toGrade":"Outperform","fromGrade":"","action":"main"},{"epochGradeDate":1598437603,"firm":"Piper Sandler","toGrade":"Overweight","fromGrade":"","action":"init"},{"epochGradeDate":1588598646,"firm":"Aegis Capital","toGrade":"Buy","fromGrade":"","action":"main"},{"epochGradeDate":1588587999,"firm":"SVB Leerink","toGrade":"Outperform","fromGrade":"","action":"main"},{"epochGradeDate":1585817240,"firm":"Citigroup","toGrade":"Buy","fromGrade":"","action":"main"},{"epochGradeDate":1585676067,"firm":"Stifel","toGrade":"Hold","fromGrade":"","action":"main"},{"epochGradeDate":1585659104,"firm":"Oppenheimer","toGrade":"Perform","fromGrade":"Underperform","action":"up"},{"epochGradeDate":1585654209,"firm":"Goldman Sachs","toGrade":"Neutral","fromGrade":"Buy","action":"down"},{"epochGradeDate":1585646345,"firm":"Jefferies","toGrade":"Hold","fromGrade":"Buy","action":"down"},{"epochGradeDate":1584092487,"firm":"Goldman Sachs","toGrade":"Buy","fromGrade":"Neutral","action":"up"},{"epochGradeDate":1583163508,"firm":"Cowen & Co.","toGrade":"Outperform","fromGrade":"","action":"init"},{"epochGradeDate":1582722640,"firm":"Oppenheimer","toGrade":"Underperform","fromGrade":"","action":"main"},{"epochGradeDate":1582022781,"firm":"Citigroup","toGrade":"Buy","fromGrade":"Neutral","action":"up"},{"epochGradeDate":1578311412,"firm":"JP Morgan","toGrade":"Neutral","fromGrade":"","action":"init"},{"epochGradeDate":1576523549,"firm":"Oppenheimer","toGrade":"Underperform","fromGrade":"","action":"main"},{"epochGradeDate":1576508203,"firm":"Stifel","toGrade":"Hold","fromGrade":"Buy","action":"down"},{"epochGradeDate":1574249344,"firm":"Oppenheimer","toGrade":"Underperform","fromGrade":"","action":"init"},{"epochGradeDate":1574080080,"firm":"Citi","toGrade":"Neutral","fromGrade":"Buy","action":"down"},{"epochGradeDate":1572529285,"firm":"Aegis Capital","toGrade":"Buy","fromGrade":"","action":"init"},{"epochGradeDate":1571135970,"firm":"Goldman Sachs","toGrade":"Neutral","fromGrade":"","action":"init"},{"epochGradeDate":1553251840,"firm":"Stifel Nicolaus","toGrade":"Buy","fromGrade":"","action":"init"},{"epochGradeDate":1541164830,"firm":"Citigroup","toGrade":"Neutral","fromGrade":"Buy","action":"down"},{"epochGradeDate":1539777585,"firm":"Citigroup","toGrade":"Buy","fromGrade":"Buy","action":"main"},{"epochGradeDate":1537881077,"firm":"Jefferies","toGrade":"Buy","fromGrade":"Buy","action":"main"},{"epochGradeDate":1537874265,"firm":"Citigroup","toGrade":"Buy","fromGrade":"Buy","action":"main"},{"epochGradeDate":1476872074,"firm":"Citigroup","toGrade":"Buy","fromGrade":"","action":"init"},{"epochGradeDate":1475656296,"firm":"Cantor Fitzgerald","toGrade":"Buy","fromGrade":"","action":"init"},{"epochGradeDate":1475615452,"firm":"Cantor Fitzgerald","toGrade":"Buy","fromGrade":"","action":"init"},{"epochGradeDate":1463037254,"firm":"Jefferies","toGrade":"Buy","fromGrade":"","action":"init"},{"epochGradeDate":1426145107,"firm":"H.C. Wainwright","toGrade":"Buy","fromGrade":"","action":"up"},{"epochGradeDate":1424252755,"firm":"SunTrust Robinson Humphrey","toGrade":"Buy","fromGrade":"Neutral","action":"up"},{"epochGradeDate":1415610000,"firm":"Citigroup","toGrade":"Neutral","fromGrade":"","action":"main"},{"epochGradeDate":1399879752,"firm":"Citigroup","toGrade":"Neutral","fromGrade":"Buy","action":"down"},{"epochGradeDate":1393584370,"firm":"Aegis Capital","toGrade":"Hold","fromGrade":"","action":"main"},{"epochGradeDate":1389888000,"firm":"MKM Partners","toGrade":"Neutral","fromGrade":"Buy","action":"down"},{"epochGradeDate":1383893330,"firm":"Citigroup","toGrade":"Buy","fromGrade":"Neutral","action":"up"},{"epochGradeDate":1383148800,"firm":"Leerink Swann","toGrade":"Market Perform","fromGrade":"Outperform","action":"down"},{"epochGradeDate":1383130853,"firm":"Aegis Capital","toGrade":"Hold","fromGrade":"","action":"main"},{"epochGradeDate":1382080843,"firm":"Citigroup","toGrade":"Neutral","fromGrade":"Buy","action":"down"},{"epochGradeDate":1382025600,"firm":"H.C. Wainwright","toGrade":"Neutral","fromGrade":"Buy","action":"down"},{"epochGradeDate":1381991178,"firm":"JP Morgan","toGrade":"Neutral","fromGrade":"Overweight","action":"down"},{"epochGradeDate":1381990292,"firm":"Canaccord Genuity","toGrade":"Hold","fromGrade":"Buy","action":"down"},{"epochGradeDate":1381943909,"firm":"Leerink Swann","toGrade":"Outperform","fromGrade":"","action":"main"},{"epochGradeDate":1381939883,"firm":"Aegis Capital","toGrade":"Hold","fromGrade":"Buy","action":"down"},{"epochGradeDate":1379401701,"firm":"Goldman Sachs","toGrade":"Neutral","fromGrade":"","action":"init"},{"epochGradeDate":1378280947,"firm":"SunTrust Robinson Humphrey","toGrade":"Buy","fromGrade":"","action":"init"},{"epochGradeDate":1376378215,"firm":"H.C. Wainwright","toGrade":"Buy","fromGrade":"Neutral","action":"up"},{"epochGradeDate":1371744899,"firm":"Oppenheimer","toGrade":"Perform","fromGrade":"","action":"init"},{"epochGradeDate":1362380154,"firm":"Citigroup","toGrade":"Buy","fromGrade":"","action":"main"},{"epochGradeDate":1357633828,"firm":"Jefferies","toGrade":"Buy","fromGrade":"","action":"main"},{"epochGradeDate":1354895044,"firm":"Aegis Capital","toGrade":"Buy","fromGrade":"","action":"main"},{"epochGradeDate":1354877921,"firm":"Canaccord Genuity","toGrade":"Buy","fromGrade":"","action":"main"},{"epochGradeDate":1354876024,"firm":"UBS","toGrade":"Neutral","fromGrade":"","action":"main"},{"epochGradeDate":1353999120,"firm":"Citigroup","toGrade":"Buy","fromGrade":"","action":"init"},{"epochGradeDate":1350293700,"firm":"JP Morgan","toGrade":"Overweight","fromGrade":"","action":"main"},{"epochGradeDate":1349248560,"firm":"Wedbush","toGrade":"Neutral","fromGrade":"Outperform","action":"down"},{"epochGradeDate":1344507000,"firm":"Canaccord Genuity","toGrade":"Buy","fromGrade":"","action":"main"},{"epochGradeDate":1341812820,"firm":"Aegis Capital","toGrade":"Buy","fromGrade":"","action":"init"},{"epochGradeDate":1340780880,"firm":"Jefferies","toGrade":"Buy","fromGrade":"","action":"main"}],"maxAge":86400},"pageViews":{"shortTermTrend":"DOWN","midTermTrend":"UP","longTermTrend":"UP","maxAge":1}}"""
        # data = json.loads(symbol)
        data = json.loads(symbol.text)
        with open('all.txt', 'a', encoding='utf8') as f:
            f.write(symbol.text + '\n')

        # summaryDetail - priceToSalesTrailing12Months - raw
        try:
            if not str(data['summaryDetail']['priceToSalesTrailing12Months']).__contains__('-'):
                if sign_ps == '>':
                    if float(data['summaryDetail']['priceToSalesTrailing12Months']['raw']) > target_ps:
                        print(color_red_to_print + 'Skip due to high P/S: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
                else:
                    if float(data['summaryDetail']['priceToSalesTrailing12Months']['raw']) < target_ps:
                        print(color_red_to_print + 'Skip due to low P/S: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
            else:
                print(color_red_to_print + 'Skip due to negative P/S: ' + companies[j][0])
                companies.remove(companies[j])
                continue
        except KeyError:
            print(color_red_to_print + 'Skip due to unavailable P/S: ' + companies[j][0])
            companies.remove(companies[j])
            continue

        # defaultKeyStatistics - trailingEps - raw
        try:
            if not str(data['defaultKeyStatistics']['trailingEps']).__contains__('-'):
                if sign_eps == '<':
                    if float(data['defaultKeyStatistics']['trailingEps']['raw']) < target_eps:
                        print(color_red_to_print + 'Skip due to low EPS: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
                else:
                    if float(data['defaultKeyStatistics']['trailingEps']['raw']) > target_eps:
                        print(color_red_to_print + 'Skip due to high EPS: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
            else:
                print(color_red_to_print + 'Skip due to negative EPS: ' + companies[j][0])
                companies.remove(companies[j])
                continue
        except KeyError:
            print(color_red_to_print + 'Skip due to unavailable EPS: ' + companies[j][0])
            companies.remove(companies[j])
            continue

        # financialData - returnOnEquity, returnOnAssets, priceToBook - raw
        try:
            if sign_roe == '<':
                if float(data['financialData']['returnOnEquity']['raw']) < target_roe:
                    print(color_red_to_print + 'Skip due to low return on equity: ' + companies[j][0])
                    companies.remove(companies[j])
                    continue
            else:
                if float(data['financialData']['returnOnEquity']['raw']) > target_roe:
                    print(color_red_to_print + 'Skip due to high return on equity: ' + companies[j][0])
                    companies.remove(companies[j])
                    continue
            if sign_roa == '<':
                if float(data['financialData']['returnOnAssets']['raw']) < target_roa:
                    print(color_red_to_print + 'Skip due to low return on assets: ' + companies[j][0])
                    companies.remove(companies[j])
                    continue
            else:
                if float(data['financialData']['returnOnAssets']['raw']) > target_roa:
                    print(color_red_to_print + 'Skip due to high return on assets: ' + companies[j][0])
                    companies.remove(companies[j])
                    continue
            if sign_roe == '<' and sign_roa == '<':
                if (float(data['financialData']['returnOnEquity']['raw']) < 2 * target_roe or
                        float(data['financialData']['returnOnAssets']['raw']) < 2 * target_roa):
                    # defaultKeyStatistics - - raw
                    if sign_pb == '>':
                        if float(data['defaultKeyStatistics']['priceToBook']['raw']) > target_pb:
                            print(color_red_to_print + 'Skip due to high P/B: ' + companies[j][0])
                            companies.remove(companies[j])
                            continue
                    else:
                        if float(data['defaultKeyStatistics']['priceToBook']['raw']) < target_pb:
                            print(color_red_to_print + 'Skip due to low P/B: ' + companies[j][0])
                            companies.remove(companies[j])
                            continue
            else:
                print(color_red_to_print + 'P/B should be considered only if ROE and ROA'
                                           ' are searched with a less than sign (<): ' + companies[j][0])
                companies.remove(companies[j])
                continue
        except KeyError:
            print(color_red_to_print + 'Skip due to unavailable ROE or ROA or P/B: ' + companies[j][0])
            companies.remove(companies[j])
            continue

        # price - marketCap - raw
        try:
            if sign_market_cap == '<':
                if float(data['price']['marketCap']['raw']) < target_market_cap:
                    print(color_red_to_print + 'Skip due to low market cap: ' + companies[j][0])
                    companies.remove(companies[j])
                    continue
            else:
                if float(data['price']['marketCap']['raw']) > target_market_cap:
                    print(color_red_to_print + 'Skip due to high market cap: ' + companies[j][0])
                    companies.remove(companies[j])
                    continue
        except KeyError:
            print(color_red_to_print + 'Skip due to unavailable market cap: ' + companies[j][0])
            companies.remove(companies[j])
            continue

        # defaultKeyStatistics - forwardPE - raw
        try:
            if not str(data['defaultKeyStatistics']['forwardPE']['raw']).__contains__('-'):
                if sign_pe == '>':
                    if float(data['defaultKeyStatistics']['forwardPE']['raw']) > target_pe:
                        print(color_red_to_print + 'Skip due to high P/E: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
                else:
                    if float(data['defaultKeyStatistics']['forwardPE']['raw']) < target_pe:
                        print(color_red_to_print + 'Skip due to low P/E: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
            else:
                print(color_red_to_print + 'Skip due to negative P/E: ' + companies[j][0])
                companies.remove(companies[j])
                continue
        except KeyError:
            print(color_red_to_print + 'Skip due to unavailable P/E: ' + companies[j][0])
            companies.remove(companies[j])
            continue

        # financialData - ebitda - raw
        try:
            if not str(data['financialData']['ebitda']['raw']).__contains__('-'):
                if sign_ebitda == '<':
                    if float(data['financialData']['ebitda']['raw']) < target_ebitda:
                        print(color_red_to_print + 'Skip due to low EBITDA: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
                else:
                    if float(data['financialData']['ebitda']['raw']) > target_ebitda:
                        print(color_red_to_print + 'Skip due to high EBITDA: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
            else:
                print(color_red_to_print + 'Skip due to negative EBITDA: ' + companies[j][0])
                companies.remove(companies[j])
                continue
        except KeyError:
            print(color_red_to_print + 'Skip due to unavailable EBITDA: ' + companies[j][0])
            companies.remove(companies[j])
            continue

        # financialData - totalDebt - raw
        try:
            if sign_total_debt == '>':
                if float(data['financialData']['totalDebt']['raw']) > target_total_debt:
                    print(color_red_to_print + 'Skip due to high total debt: ' + companies[j][0])
                    companies.remove(companies[j])
                    continue
            else:
                if float(data['financialData']['totalDebt']['raw']) < target_total_debt:
                    print(color_red_to_print + 'Skip due to low total debt: ' + companies[j][0])
                    companies.remove(companies[j])
                    continue
        except KeyError:
            print(color_red_to_print + 'Skip due to unavailable total debt: ' + companies[j][0])
            companies.remove(companies[j])
            continue

        # financialData - revenuePerShare - raw
        try:
            if not str(data['financialData']['revenuePerShare']['raw']).__contains__('-'):
                if sign_ebitda == '>':
                    if float(data['financialData']['revenuePerShare']['raw']) > target_rps:
                        print(color_red_to_print + 'Skip due to high RPS: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
                else:
                    if float(data['financialData']['revenuePerShare']['raw']) < target_rps:
                        print(color_red_to_print + 'Skip due to low RPS: ' + companies[j][0])
                        companies.remove(companies[j])
                        continue
            else:
                print(color_red_to_print + 'Skip due to negative RPS: ' + companies[j][0])
                companies.remove(companies[j])
                continue
        except KeyError:
            print(color_red_to_print + 'Skip due to unavailable RPS: ' + companies[j][0])
            companies.remove(companies[j])
            continue

        # summaryProfile -
        companies[j].append(data['summaryProfile']['sector'].replace('—', '-').replace(',', '-'))

        # summaryProfile -
        companies[j].append(data['summaryProfile']['industry'].replace('—', '-').replace(',', '-'))

        # financialData - currentPrice - raw
        companies[j].append(float(data['financialData']['currentPrice']['raw']))

        print(color_green_to_print + str(companies[j]))
        append_company_output(companies[j])
        j += 1


def count_number_of_stocks_using_number_of_companies(amount_in_usd: int):
    percentage = round(1 / len(companies), 5)
    amount_for_company = round(amount_in_usd * percentage, 5)
    for i in range(len(companies)):
        number_of_stocks = float(amount_for_company) // float(companies[i][3])
        companies[i].append(int(number_of_stocks))


def update_data():
    read_csv_results()

    # read_csv_and_fill_data()
    # prepare_output_file()
    # get_data_yf()
    # count_number_of_stocks_using_number_of_companies(16000)
    # append_number_of_stocks_output()


def print_data(event):
    global rb_pe, pe, rb_ps, ps, rb_pb, pb, rb_eps, eps, rb_ebitda, ebitda, rb_debt, debt, rb_rps, rps, \
        rb_roe, roe, rb_roa, roa, rb_cap, cap
    print(rb_pe.get())
    print(pe.get())

    # get_data_yf() @todo


if __name__ == '__main__':
    start_timer = get_current_time_milliseconds()
    update_data()
    end_timer = get_current_time_milliseconds()
    time_of_running = end_timer - start_timer
    print(color_green_to_print + 'Time of running in milliseconds: ' + str(time_of_running))
    print(color_green_to_print + 'Time of running in seconds: ' + str(time_of_running / 1000))

    window = Tk()
    window.title('Market stocks calculator')
    window.minsize(400, 250)
    window.maxsize(2880, 1620)
    window.iconphoto(False, PhotoImage(file='logo.png'))

    length_of_columns = []
    for x in range(len(companies[0]) - 2):
        length_of_columns.append(len(companies[0][x]))
    length_of_columns.append(None)
    length_of_columns.append(None)
    table = Table(master=window, height=600, column_headers=companies[0], column_min_widths=length_of_columns)
    table.pack(side=LEFT)

    table.set_data(companies[1:])
    table.insert_row(['WWWWW', 'F', 'A', 100.0, 2])
    window.update()

    frame_settings = Frame()
    counter_row = 0
    counter_column = 0

    label_filters = Label(master=frame_settings, text='Filters')
    label_filters.grid(row=counter_row, column=counter_column + 1)
    counter_row += 1
    rb_pe, pe = create_filter(frame_settings, 'P/E:')
    rb_ps, ps = create_filter(frame_settings, 'P/S:')
    rb_eps, eps = create_filter(frame_settings, 'EPS:')
    rb_ebitda, ebitda = create_filter(frame_settings, 'EBITDA:')
    rb_debt, debt = create_filter(frame_settings, 'Total debt:')
    rb_rps, rps = create_filter(frame_settings, 'RPS:')
    rb_roe, roe = create_filter(frame_settings, 'ROE:')
    rb_roa, roa = create_filter(frame_settings, 'ROA:')
    rb_pb, pb = create_filter(frame_settings, 'P/B:')
    rb_cap, cap = create_filter(frame_settings, 'Market capitalization:')

    btn_confirm = Button(master=frame_settings, text='Confirm')
    btn_confirm.grid(row=counter_row, column=counter_column)
    btn_confirm.bind('<Button-1>', print_data)

    frame_settings.pack()
    window.state('zoomed')
    window.mainloop()
