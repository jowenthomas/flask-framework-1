from flask import Flask, render_template, flash, redirect, url_for
from config import Config
from forms import SubmitForm
import os

#for api with heroku environment
from boto.s3.connection import S3Connection
conn = S3Connection(os.environ['api_key'])


app = Flask(__name__)
app.config.from_object(Config)



@app.route('/', methods=['GET', 'POST'])
def index():
    form = SubmitForm()
    if form.validate_on_submit():
        company = form.tickerName.data
        return redirect(url_for('plot', company=company))
    return render_template('index.html', title="Enter a company's ticker:", form=form)

@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/plot/<company>')
def plot(company):
    import json
    import requests
    import pandas as pd

    from bokeh.models import ColumnDataSource, PreText
    from bokeh.plotting import figure
    from bokeh.resources import CDN
    from bokeh.embed import components


    ticker = company
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}&outputsize=compact'.format(
        ticker, api_key)

    # get data from api
    apiresponse = requests.get(url)

    # easier, i think, to clean up the dictionary with python before passing into pandas
    dictio = apiresponse.json()
    dictio.pop('Meta Data')
    close_dict = {key: value['4. close'] for key, value in dictio['Time Series (Daily)'].items()}

    # setup and clean df
    df = pd.DataFrame(close_dict.items(), columns=['date', 'close'])
    df['date'] = pd.to_datetime(df['date'])
    # limit to 30
    df = df.iloc[0:30]

    # setup figure for bokeh
    source = ColumnDataSource(df)

    p = figure(title="Closing Price: Previous 30 Days", x_axis_label='Date', x_axis_type='datetime',
               y_axis_label='CLosing Price (USD)')
    p.line(x='date', y='close', legend_label=ticker, source=source, line_width=2)

    # setup stats summary
    stats_text = str(pd.to_numeric(df['close']).describe())
    stats_text = stats_text[:-29]
    pre = PreText(text=stats_text, width=500, height=100)

    script1, div1 = components(p)
    script2, div2 = components(pre)
    cdn_js = CDN.js_files[0]
    cdn_widg = CDN.js_files[1]
    cdn_css = CDN.css_files
    return render_template("plot.html", script1=script1, div1=div1, script2=script2, div2=div2,
                           cdn_js=cdn_js, cdn_widg=cdn_widg, cdn_css=cdn_css)


if __name__ == "__main__":
    app.run()
