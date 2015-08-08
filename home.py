from flask import Flask, render_template, request
import linker
app = Flask(__name__)
app.debug = True

@app.route("/")
def home():
	return render_template('home.html')

@app.route("/link")
def link():
	args = request.args
	link = linker.find_link(args['star1'], args['star2'])
	return render_template('link.html', link=link)


if __name__ == "__main__":
	app.run(host='0.0.0.0')