def get_current_time_milliseconds():
    import time
    return round(time.time() * 1000)


companies = []
target_net_income = 0
target_pb = 3
target_ps = 10
target_eps = 1
target_roe = 0.1
target_roa = 0.05
target_pe = 30
target_market_cap = 1_000_000_000

color_green_to_print = '\033[1;92m'
color_red_to_print = '\033[1;91m'


def read_csv_and_fill_data():
    import os
    import re
    root_dir = os.getcwd()
    if os.path.exists('results.csv'):
        os.remove('results.csv')
    regex = re.compile('.*csv$')

    for root, dirs, files in os.walk(root_dir):
        index = 0
        for file in files:
            if regex.match(file):
                with open(file, 'r', encoding='utf8') as f:
                    for line in f:
                        if line.__contains__('Symbol'):
                            continue
                        companies.append([])
                        _, symbol, sector, industry = list(line.split(','))
                        industry = industry.replace('\n', '')
                        companies[index].append(symbol)
                        companies[index].append(sector)
                        companies[index].append(industry)
                        index += 1


def read_csv_results():
    index = 0
    with open('results.csv', 'r', encoding='utf8') as f:
        for line in f:
            if line.__contains__('Symbol'):
                continue
            companies.append([])
            symbol, cap, pe, price, nums, perc, sector = list(line.split(','))
            cap = int(cap)
            pe = float(pe)
            price = float(price)
            nums = int(nums)
            perc = float(perc)
            sector = sector.replace('\n', '')
            companies[index].append(symbol) \
                .append(sector) \
                .append(cap) \
                .append(pe) \
                .append(price) \
                .append(nums) \
                .append(perc)
            del symbol, cap, pe, price, sector, nums, perc
            index += 1


def write_output():
    with open('results.csv', 'w') as f:
        f.write('Symbol,Sector,Industry,Current/last price in USD,Number of shares\n')
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
    import yfinance as yfl
    j = 0
    while j < len(companies):
        symbol = yfl.Ticker(companies[j][0]).info
        if symbol.keys().__contains__('netIncomeToCommon'):
            if symbol['netIncomeToCommon'] < target_net_income:
                print(color_red_to_print + 'Skip due to negative net income: ' + companies[j][0])
                companies.remove(companies[j])
                continue

        if symbol.keys().__contains__('totalDebt') and symbol['totalDebt'] is not None:
            if symbol['netIncomeToCommon'] / symbol['totalDebt'] < 0.3:
                print(color_red_to_print + 'Skip due to low coefficient net income/total debt: ' + companies[j][0])
                companies.remove(companies[j])
                continue

        if symbol.keys().__contains__('priceToSalesTrailing12Months') \
                and symbol['priceToSalesTrailing12Months'] is not None:
            if symbol['priceToSalesTrailing12Months'] > target_ps:
                print(color_red_to_print + 'Skip due to high p/s: ' + companies[j][0])
                companies.remove(companies[j])
                continue

        if symbol.keys().__contains__('trailingEps') \
                and symbol['trailingEps'] is not None \
                and symbol.keys().__contains__('forwardEps') \
                and symbol['forwardEps'] is not None:
            if symbol['trailingEps'] < 1 or symbol['forwardEps'] < target_eps:
                print(color_red_to_print + 'Skip due to low eps: ' + companies[j][0])
                companies.remove(companies[j])
                continue

        if symbol.keys().__contains__('returnOnEquity') and symbol['returnOnEquity'] is not None and \
                symbol.keys().__contains__('returnOnAssets') and symbol['returnOnAssets'] is not None:
            if symbol['returnOnEquity'] < target_roe or symbol['returnOnAssets'] < target_roa:
                print(color_red_to_print + 'Skip due to low return on equity/assets: ' + companies[j][0])
                companies.remove(companies[j])
                continue
            elif (symbol['returnOnEquity'] < 2 * target_roe or symbol['returnOnAssets'] < 2 * target_roa) and \
                    symbol.keys().__contains__('priceToBook') and symbol['priceToBook'] is not None:
                if symbol['priceToBook'] > target_pb:
                    print(color_red_to_print + 'Skip due to high p/b: ' + companies[j][0])
                    companies.remove(companies[j])
                    continue

        if symbol.keys().__contains__('marketCap') and symbol['marketCap'] is not None:
            if symbol['marketCap'] < target_market_cap:
                print(color_red_to_print + 'Skip due to low market cap: ' + companies[j][0])
                companies.remove(companies[j])
                continue

        if symbol.keys().__contains__('trailingPE') and symbol['trailingPE'] is not None:
            if symbol['trailingPE'] > target_pe:
                print(color_red_to_print + 'Skip due to high p/e: ' + companies[j][0])
                companies.remove(companies[j])
                continue
        elif symbol.keys().__contains__('forwardPE') and symbol['forwardPE'] is not None:
            if symbol['forwardPE'] > target_pe:
                print(color_red_to_print + 'Skip due to high p/e: ' + companies[j][0])
                companies.remove(companies[j])
                continue
        else:
            print(color_red_to_print + 'Skip due to unavailable p/e: ' + companies[j][0])
            companies.remove(companies[j])
            continue

        if symbol.keys().__contains__('currentPrice'):
            companies[j].append(symbol['currentPrice'])

        print(color_green_to_print + str(companies[j]))
        j += 1


def count_number_of_shares_using_number_of_companies(amount_in_usd: int):
    percentage = round(1 / len(companies), 5)
    amount_for_company = round(amount_in_usd * percentage, 5)
    for i in range(len(companies)):
        number_of_shares = float(amount_for_company) // float(companies[i][3])
        companies[i].append(int(number_of_shares))


def update_data():
    read_csv_and_fill_data()
    get_data_yf()
    sort_by_sector()
    count_number_of_shares_using_number_of_companies(16000)
    write_output()


if __name__ == '__main__':
    start_timer = get_current_time_milliseconds()

    # companies = [['AAPL'], ['GE'], ['XOM'], ['BABA'], ['TSLA'], ['SPCE'], ['GOOG'], ['BRK-B']]
    # companies = [['TSM']]
    # get_data_yf()
    # count_number_of_shares_using_number_of_companies(16000)
    # write_output()
    # import yfinance as yfl
    # for j in range(len(companies)):
    #     symbol = yfl.Ticker(companies[j][0]).info
    #     print(symbol)
    # print(companies)

    update_data()
    # read_csv_results()

    end_timer = get_current_time_milliseconds()
    time_of_running = end_timer - start_timer
    print(color_green_to_print + 'Time of running in milliseconds: ' + str(time_of_running))
