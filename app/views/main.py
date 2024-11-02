from flask import Blueprint,render_template,flash,redirect,url_for,request
from app.forms.forms import LoginForm, RegistrationForm, ShortURLForm
from app.models.models import AppUser, ShortURL
from flask_login import current_user, login_user, logout_user, login_required
from app import db
import app
import sqlalchemy as sa
from urllib.parse import urlsplit


main_bp = Blueprint('main', __name__)

@main_bp.route('/index', methods=['GET','POST'])
@main_bp.route('/', methods=['GET','POST'])
@login_required
def index():
    form = ShortURLForm()

    if form.validate_on_submit():
        short_url = ShortURL(description=form.description.data, actual_url=form.actual_url.data, user_id=current_user.id)
        short_url.generate_short_url()
        db.session.add(short_url)
        db.session.commit()
        flash(f"Short URL {short_url.short_url} has been created")
        return redirect(url_for('main.index'))

    #Pagination
    page = request.args.get('page', 1, type=int)
    #urls = db.session.scalars(current_user.get_all_short_urls()).all()
    query = current_user.get_all_short_urls()
    urls = db.paginate(query, page=page, per_page=app.app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index',page=urls.next_num) if urls.has_next else None
    prev_url = url_for('main.index',page=urls.prev_num) if urls.prev_num else None

    base_url = request.base_url
    return render_template('index.html', title='Home', urls=urls, form=form, base_url=base_url,next_url=next_url,prev_url=prev_url,curr_page='index')

@main_bp.route('/all')
@login_required
def all():
    page = request.args.get('page', 1, type=int)
    #urls = db.session.scalars(current_user.get_all_short_urls()).all()
    #query = current_user.get_all_short_urls()
    #query = sa.select(ShortURL).join(AppUser, ShortURL.user_id == AppUser.id)
    #query =  db.session.query(AppUser)/k
    query = (
        db.session.query(ShortURL, AppUser)
        .join(AppUser, ShortURL.user_id == AppUser.id)
    )
    urls = db.paginate(query, page=page, per_page=app.app.config['POSTS_PER_PAGE'], error_out=False)
    #urls = query.all()
    next_url = url_for('main.all',page=urls.next_num) if urls.has_next else None
    prev_url = url_for('main.all',page=urls.prev_num) if urls.prev_num else None

    base_url = request.base_url
    return render_template('index.html', title='All', urls=urls, base_url=base_url,next_url=next_url,prev_url=prev_url,curr_page='all')

@main_bp.route('/shorturl/<id>', methods=["POST"])
@login_required
def shorturl_delete(id):
    curr_user_id = current_user.id

    short_url = ShortURL.query.get(id)
    if short_url is None or curr_user_id != short_url.user_id:
        flash('Failed to delete the URL. You may not have permission or the URL does not exist.', 'warning')
        return redirect(url_for('main.index'))

    db.session.delete(short_url)
    db.session.commit()
    return redirect(url_for('main.index'))

@main_bp.route('/<short_key>',methods=['GET'])
def redirect_to_url(short_key):
    #Check DB for short URL
    #send a redirect to the given actual_url
    short_url = db.first_or_404(sa.select(ShortURL).where(ShortURL.short_url == short_key))
    return redirect(short_url.actual_url)


@main_bp.route('/test', methods=['GET','POST'])
@login_required
def test():
    return 'test good', 200

@main_bp.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@main_bp.route('/login', methods=['GET','POST'])
def login():
    #already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    #if invalid form
    if not form.validate_on_submit():
        return render_template('login.html',  title='Sign In', form=form)
    
    user = db.session.scalar(sa.select(AppUser).where(AppUser.username == form.username.data))
    if user is None or not user.check_password(form.password.data):
        flash('Invalid username or password')
        return redirect(url_for('main.login'))
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or urlsplit(next_page).netloc != '':
        next_page = url_for('main.index')
    #flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
    return redirect(url_for('main.index'))

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main_bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = AppUser(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.index'))
    return render_template('register.html', title='Register',form=form)
