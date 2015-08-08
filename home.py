from flask import Flask, render_template, request, flash
import linker
app = Flask(__name__)
app.debug = True
app.secret_key = 'shhh'

@app.route("/")
def home():
	return render_template('home.html')

@app.route("/link")
def link():
	args = request.args
	link = linker.find_link(args['star1'], args['star2'])
	if link:
		return render_template('link.html', link=link)
	else:
		flash("Not sure who you're talking about there.")
		return render_template('home.html')


if __name__ == "__main__":
	app.run(host='0.0.0.0')