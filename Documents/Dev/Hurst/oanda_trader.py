import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts
from datetime import timedelta
from datetime import datetime
from dateutil import parser

DEMO_KEY = '#INSERT DEMO KEY HERE'
ENV = 'practice'
ACCOUNT_ID = '#INSERT ACCOUNT ID HERE#'

oanda = oandapyV20.API(environment=ENV, access_token=DEMO_KEY)

to_time = datetime.utcnow() - timedelta(hours=1)
to_time = to_time.isoformat("T") + "Z"


def formatPrice(ticker, price):
    if ("JPY" in ticker):
        return format(price, '.3f')
    if ticker == "SPX500_USD":
        return format(price, '.1f')
    else:
        return format(price, '.5f')


def get_history(instrument, time_frame, count):

    history_data = []
    count_length = count

    while count_length != 0:
        if count_length > 5000:
            get_count = 5000

            if not history_data:
                params = {'granularity': time_frame, 'count': get_count}
            else:
                params = {
                    'granularity': time_frame,
                    'count': get_count,
                    'to': history_data[0]['time']
                }

            history = instruments.InstrumentsCandles(
                instrument=instrument, params=params)

            data = oanda.request(history)['candles']
            history_data = data + history_data
            count_length = count_length - get_count

        elif count_length <= 5000:
            get_count = count_length

            if not history_data:
                params = {'granularity': time_frame, 'count': get_count}
            else:
                params = {
                    'granularity': time_frame,
                    'count': get_count,
                    'to': history_data[0]['time']
                }

            history = instruments.InstrumentsCandles(
                instrument=instrument, params=params)
            data = oanda.request(history)['candles']
            history_data = data + history_data
            count_length = count_length - get_count

    return history_data


def map_history(history, complete=True):

    candles = history
    formatted_history = [{
        'Open': [],
        'Close': [],
        'Low': [],
        'High': [],
        'Volume': [],
        'Midpoint': [],
        'Daily_range': [],
        'Colour': [],
        'Date Time': []
    }]

    for candle in candles:
        if candle['complete'] is True and complete is True:

            current_candle = candle['mid']

            formatted_history[0]['Open'].append(float(current_candle['o']))
            formatted_history[0]['Close'].append(float(current_candle['c']))
            formatted_history[0]['Low'].append(float(current_candle['l']))
            formatted_history[0]['High'].append(float(current_candle['h']))
            formatted_history[0]['Volume'].append(float(candle['volume']))
            formatted_history[0]['Date Time'].append(
                str(
                    datetime.strftime(
                        parser.parse(candle['time']), "%Y-%m-%d %H:%M:%S")))

            if float(current_candle['o']) > float(current_candle['c']):
                colour = 0
            else:
                colour = 1

            formatted_history[0]['Colour'].append(colour)
            formatted_history[0]['Midpoint'].append(
                round((float(current_candle['o']) + float(current_candle['c']))
                      / 2, 4))
            formatted_history[0]['Daily_range'].append(
                round(
                    float(current_candle['h']) - float(current_candle['l']), 4))

        elif complete is False:

            current_candle = candle['mid']

            formatted_history[0]['Open'].append(float(current_candle['o']))
            formatted_history[0]['Close'].append(float(current_candle['c']))
            formatted_history[0]['Low'].append(float(current_candle['l']))
            formatted_history[0]['High'].append(float(current_candle['h']))
            formatted_history[0]['Volume'].append(float(candle['volume']))
            formatted_history[0]['Date Time'].append(
                str(
                    datetime.strftime(
                        parser.parse(candle['time']), "%Y-%m-%d %H:%M:%S")))

            if float(current_candle['o']) > float(current_candle['c']):
                colour = 0
            else:
                colour = 1

            formatted_history[0]['Colour'].append(colour)
            formatted_history[0]['Midpoint'].append(
                round((float(current_candle['o']) + float(current_candle['c']))
                      / 2, 4))
            formatted_history[0]['Daily_range'].append(
                round(
                    float(current_candle['h']) - float(current_candle['l']), 4))

    return formatted_history


def place_trailing_order(data):
    i = 0
    while i <= 10:
        try:
            daysToExpiry = data['days_to_expiry']
            instrument = data['instrument']
            units = data['units']
            orderType = data['order_type']
            entryPrice = data['entry_price']
            trailingPrice = data['stop_price']
            profitPrice = data['profit_price']

            trade_expire = datetime.utcnow() + timedelta(days=daysToExpiry)
            trade_expire = trade_expire.isoformat("T") + "Z"

            formattedEntryPrice = formatPrice(instrument, entryPrice)
            formattedProfitPrice = formatPrice(instrument, profitPrice)

            formattedStopPrice = abs(entryPrice - trailingPrice)
            # formattedEntryPrice = format(entryPrice, '.5f')
            # formattedProfitPrice = format(profitPrice, '.5f')

            # Negative units for shorting
            data = {
                'order': {
                    'instrument': instrument,
                    'units': units,
                    'type': orderType,
                    'price': formattedEntryPrice,
                    'gtdTime': trade_expire,
                    'trailingStopLossOnFill': {
                        'distance': formattedStopPrice
                    },
                    'takeProfitOnFill': {
                        'price': formattedProfitPrice
                    }
                }
            }

            createOrder = orders.OrderCreate(ACCOUNT_ID, data=data)
            order = oanda.request(createOrder)
            return order
        except oandapyV20.exceptions.V20Error as err:
            if err.code == 429:
                continue
            else:
                print(err)
                raise
    else:
        print("It fucked bro")


def get_account_info():
    i = 0
    while i <= 10:
        try:
            accountSummary = accounts.AccountSummary(accountID=ACCOUNT_ID)
            summary = oanda.request(accountSummary)
            return summary['account']
        except oandapyV20.exceptions.V20Error as err:
            if err.code == 429:
                continue
    else:
        print("It fucked bro")
