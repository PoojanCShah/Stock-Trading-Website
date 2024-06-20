function check_symbols() {
    let checkbox;
    for (let index = 0; index < symbols.length; index++) {
        const symbol = symbols[index];
        checkbox = document.querySelector(`input[value="${symbol}"]`);
        checkbox.checked = true;
    }
}
function hideElements() {
    let all_symbols_check_box = document.querySelectorAll(".checkbox-group");
    let search = document.getElementById("search");
    for (let i = 0; i < all_symbols_check_box.length; i++) {
        let s_check = all_symbols_check_box[i];
        if (s_check.textContent.toLowerCase().includes(search.value.toLowerCase())) {
            s_check.style.display = "";
        } else {
            s_check.style.display = "none";
        }
    }
}
function data_dict_to_arrays(symbol) {
    let data_symbol = plot_data[symbol];
    let dates = [];
    let close = [];
    let open = [];
    let high = [];
    let low = [];
    let vwap = [];
    let volume = [];
    let previous_close = [];
    let colors = [];
    data_symbol.forEach(row => {
        dates.push(row.CH_TIMESTAMP);
        close.push(row.CH_CLOSING_PRICE);
        open.push(row.CH_OPENING_PRICE);
        high.push(row.CH_TRADE_HIGH_PRICE);
        low.push(row.CH_TRADE_LOW_PRICE);
        vwap.push(row.VWAP);
        volume.push(row.CH_TOTAL_TRADES);
        previous_close.push(row.CH_PREVIOUS_CLS_PRICE);
        colors.push(row.CH_CLOSING_PRICE > row.CH_PREVIOUS_CLS_PRICE ? "green" : "red");
    });
    return [dates, close, open, high, low, vwap, volume, previous_close, colors];
}

function plot_normal() {
    let traces = [];
    symbols.forEach((symbol, index) => {

        let [dates, close, open, high, low, vwap, volume, previous_close, colors] = data_dict_to_arrays(symbol);


        let trace = {
            x: dates,
            y: close,
            text: close.map(function (x, index) {
                return 'Close: ' + x + '<br>Open: ' + open[index] + '<br>High: ' + high[index] + '<br>Low: ' + low[index] + '<extra></extra>';
            }),
            mode: 'lines',
            name: symbol,
            line: {
                width: 2,
            },
            type: 'scatter',
            hovertemplate: '%{text}'
        };
        traces.push(trace);
    });
    var layout = {
        title: 'Stock Price Trends',
        plot_bgcolor: '#f8f8f8',
        xaxis: {
            title: 'Date',
            tickformat: "%Y-%m-%d",
            rangeslider: {visible: true},
        },
        yaxis: {
            title: 'Closing Price',
        },
        width: 1500,
        height: 650,
        hovermode: 'closest',
        font: { family: 'sans-serif', size: 14, color: 'black' }
    };
    Plotly.newPlot('graph', traces, layout);
    let legend = {
        x: 0,
        y: 1,
        traceorder: 'normal',
        orientation: 'h',
    };

    let config = {
        responsive: true,
    };

    Plotly.update('graph', { legend }, layout, config);
}

function plot_volume() {

    let [dates, close, open, high, low, vwap, volume, previous_close, colors] = data_dict_to_arrays(symbols[0]);

    let trace_volume = {
        x: dates,
        y: volume,
        type: 'bar',
        marker: {
            color: colors,
            opacity: 0.5,
        },
    };
    let layout = {
        title: 'Stock Volume Trends',
        xaxis: {
            title: 'Date',
            tickformat: "%Y-%m-%d",
            rangeslider: {visible: true},
        },
        yaxis: {
            title: 'Volume',
        },
        width: 1500,
        height: 650,
        hovermode: 'closest',
        bargap: 0, // No gap between bars
    };

    Plotly.newPlot('graph', [trace_volume], layout);
}

function plot_relative() {
    let traces = [];
    symbols.forEach((symbol, index) => {

        let [dates, close, open, high, low, vwap, volume, previous_close, colors] = data_dict_to_arrays(symbol);

        let max_price = Math.max(...close);
        let relative_values = close.map(price => (100 * price) / max_price);

        // Create a trace for the current symbol
        let trace = {
            x: dates,
            y: relative_values,
            text: close.map(function (x, index) {
                return 'Close: ' + x + '<br>Open: ' + open[index] + '<br>High: ' + high[index] + '<br>Low: ' + low[index] + '<extra></extra>';
            }),
            mode: 'lines',
            name: symbol,
            line: {
                width: 2,
            },
            type: 'scatter',
            hovertemplate: '%{text}'
        };

        traces.push(trace);
    });

    let layout = {
        title: 'Stock Price Trends',
        xaxis: {
            title: 'Date',
            tickformat: "%Y-%m-%d",
            rangeslider: {visible: true},
        },
        yaxis: {
            title: 'Relative Closing Price',
        },
        width: 1500,
        height: 650,
        hovermode: 'closest',
    };
    Plotly.newPlot('graph', traces, layout);
    let legend = {
        x: 0,
        y: 1,
        traceorder: 'normal',
        orientation: 'h',
    };

    let config = {
        responsive: true,
    };

    Plotly.update('graph', { legend }, layout, config);
}



function plot_candlestick() {
    let traces = [];
    symbols.forEach((symbol, index) => {

        let [dates, close, open, high, low, vwap, volume, previous_close, colors] = data_dict_to_arrays(symbol);

        let trace = {
            x: dates,
            close: close,
            open: open,
            high: high,
            low: low,
            type: 'candlestick',
            name: symbol,
            increasing: { line: { color: 'green' } },
            decreasing: { line: { color: 'red' } }
        };

        traces.push(trace);
    });
    let layout = {
        title: 'Stock Price Trends',
        plot_bgcolor: '#f8f8f8',
        xaxis: {
            title: 'Date',
            tickformat: "%Y-%m-%d",
            rangeslider: {
                visible: true,
            },
        },
        yaxis: {
            title: 'Closing Price',
        },
        width: 1500,
        height: 650,
        hovermode: 'closest',
        font: { family: 'sans-serif', size: 14, color: 'black' }
    };

    Plotly.newPlot('graph', traces, layout);
    let legend = {
        x: 0,
        y: 1,
        traceorder: 'normal',
        orientation: 'h',
    };

    let config = {
        responsive: true,
    };

    Plotly.update('graph', { legend }, layout, config);
}
