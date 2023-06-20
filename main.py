from flask import Flask, request, jsonify

import config
from matching import StringMatching

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/search', methods=['GET', 'POST'])
def search():
    result = {}
    for shop in config.main_shop:
        if request.method == 'GET':
            product = request.args.get('product', '')
        if request.method == 'POST':
            product = request.json['product']

        r = StringMatching.find(product, config.main_shop[shop])
        val = r[1].loc[r[0]]["val"]
        result[config.main_shop[shop]] = {"product": val[1],
                                          "price": f"{val[2]:,}",
                                          "link": val[-1]}
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
