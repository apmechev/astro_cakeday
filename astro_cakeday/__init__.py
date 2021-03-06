import os
import datetime
import logging
import time

from flask import Flask
from flask import request
from flask import render_template 
from flask.logging import default_handler

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms import SubmitField
from wtforms import RadioField 

from astro_cakeday.populate_cal import populate_ical
from astro_cakeday.planets import Planets


##TODO: give next few birthdays

class MyForm(FlaskForm):
    name = StringField('Your Name (optional)')
    birthyear = IntegerField('Year', default=1999)
    birthmonth = IntegerField('Month', default=1)
    birthday = IntegerField('Day', default=1)
    mercury_stagger = IntegerField('Skip Mercury Birthdays by', default=5)
    venus_stagger = IntegerField('Skip Venus Birthdays by', default=2)

    cal_start = IntegerField('Start Year', default=2018)
    cal_end = IntegerField('End Year', default=2100)
    year_type =  RadioField('', 
            choices=[('sidereal','Sidereal Year'),('tropical','Tropical Year')], 
            default='tropical')
    submit = SubmitField('Submit!')


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    logging.basicConfig(filename='cakedays.space.log', level=logging.DEBUG)

    app.config.from_mapping(
        SECRET_KEY='sdafsadfsa',
    )
    UPLOAD_FOLDER = 'uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


    Bootstrap(app)
    
    app.logger.addHandler(default_handler)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def count_visitors(logfile='cakedays.space.log'):
        return open(logfile, 'r').read().count('pltf')

    @app.route('/',  methods=['GET', 'POST'])
    def hello():
        if request.user_agent:
            user_agent = request.user_agent.string
            if request.user_agent.platform:
                platform = request.user_agent.platform
            else:
                platform = ""
            if request.user_agent.browser:
                browser = request.user_agent.browser
            else:
                browser=""
        app.logger.info("visit from ip:{}, pltf:{}, brws:{}, time:{}".format(request.remote_addr,
                    platform, browser, time.time()))
        app.logger.info("full_user_agent: {}".format(user_agent))
        app.logger.info("Referrer: {}".format(request.referrer))
        form = MyForm()
        if request.method == 'POST':
            day = form.birthday.data
            month = form.birthmonth.data
            year = form.birthyear.data
            start_year = form.cal_start.data
            end_year = form.cal_end.data
            birthdate = "{}-{}-{}".format(year, month, day)
            cal_start = '{}-01-01'.format(start_year)
            cal_end = '{}-01-01'.format(end_year)
            try:
                datetime.datetime(year=year, month=month, day=day)
            except Exception as e:
                return "ERROR: the birthday year, month, or day entered could not be understood; {}".format(str(e))

            try:
                merc_stag = int(form.mercury_stagger.data)
            except:
                merc_stag = form.mercury_stagger.default
            try:
                ven_stag = int(form.venus_stagger.data)
            except:
                ven_stag = form.venus_stagger.default
            custom_staggers = {'Mercury': merc_stag,
                               'Venus': ven_stag}
            planet_period = form.year_type.data
            planets = Planets(birthdate, staggers=custom_staggers, period=planet_period)

            icalfile = populate_ical(planets, person_name=form.name.data or 'Your',  birthday=birthdate,
                                    cal_start=cal_start, cal_end=cal_end)
            return render_template('result.html', filename=icalfile, count_visitors=count_visitors)
 

        return render_template('birthday.html', form=form)

    return app
