import os
from datetime import timedelta
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import or_
from flask_cors import CORS


load_dotenv()

app = Flask(__name__)
CORS(
    app,
    origins=["http://localhost:5173"]
)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
jwt = JWTManager(app)    #创建 JWT管理器，并把它连接到当前 Flask应用

app.json.ensure_ascii = False   #它控制 Flask生成 JSON时显示中文


db_user = os.getenv("DB_USER")
db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME")


app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{db_user}:{db_password}"
    f"@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False





db = SQLAlchemy(app)
migrate = Migrate(app, db)





class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.String(255), nullable=True)
    role = db.Column(
        db.String(20),
        nullable=False,
        default="user",
    )
    status = db.Column(
        db.String(20),
        nullable=False,
        default="active",
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)




class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )




class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    category_id = db.Column(
        db.BigInteger,
        db.ForeignKey("categories.id"),
        nullable=False,
        index=True
    )
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="published")
    view_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )
    author = db.relationship("User", backref="posts")
    category = db.relationship("Category", backref="posts")





class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    post_id = db.Column(
        db.BigInteger,
        db.ForeignKey("posts.id"),
        nullable=False,
        index=True
    )
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="published")

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )
    author = db.relationship("User", backref="comments")
    post = db.relationship("Post", backref="comments")




class PostLike(db.Model):
    __tablename__ = "post_likes"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    post_id = db.Column(
        db.BigInteger,
        db.ForeignKey("posts.id"),
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,     #规定字段的数据类型
        nullable=False,
        server_default=db.func.now()
    )

    __table_args__ = (         #这是SQLAlchemy约定的特殊名称，意思是：这张表还有一些表级别的配置，同时涉及多个字段的规则，通常放进__table_args__
        #创建唯一约束
        db.UniqueConstraint(
            "user_id",
            "post_id",
            name="uq_post_likes_user_post"
        ),
    )

    user = db.relationship("User", backref="post_likes")
    post = db.relationship("Post", backref="likes")








class PostFavorite(db.Model):
    __tablename__ = "post_favorites"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    post_id = db.Column(
        db.BigInteger,
        db.ForeignKey("posts.id"),
        nullable=False,
        index=True
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "post_id",
            name="uq_post_favorites_user_post"
        ),
    )

    user = db.relationship("User", backref="post_favorites")
    post = db.relationship("Post", backref="favorites")






#api
#Application Programming Interface
#应用程序编程接口

@app.get("/api/health")
def health_check():
    return jsonify({"message": "校园论坛后端运行正常"})


@app.get("/api/db-check")
def database_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"message": "数据库连接正常"})
    except Exception:
        app.logger.exception("数据库连接失败")
        return jsonify({"message": "数据库连接失败"}), 500



@app.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"message": "用户名、邮箱和密码不能为空"}), 400

    if len(username) < 3:
        return jsonify({"message": "用户名至少需要3个字符"}), 400

    if len(password) < 8:
        return jsonify({"message": "密码至少需要8个字符"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "用户名已存在"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "邮箱已存在"}), 409

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)

    # 两个请求可能“同时进行”,比如两个人同时注册用户名，所以得再来一层保险
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "用户名或邮箱已存在"}), 409

    return jsonify(
        {
            "message": "注册成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    ), 201





#登录
@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400

    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({"message": "用户名或密码错误"}), 401
    if user.status != "active":
        return jsonify({"message": "账号已被禁用"}), 403

    access_token = create_access_token(identity=str(user.id))  #生成一个访问令牌JWT   JWT标准要求 sub（subject，主体）使用字符串。

    return jsonify(
        {
            "message": "登录成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "access_token": access_token,
            },
        }
    ), 200




@app.get("/api/auth/me")
@jwt_required()    #表示这个接口必须携带有效 JWT。没有令牌、令牌错误或过期时，Flask-JWT-Extended会在进入函数前拒绝请求
def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if user is None:
        return jsonify({"message": "用户不存在"}), 404
    if user.status != "active":
        return jsonify({"message": "账号已被禁用"}), 403
    return jsonify(
        {
            "message": "获取当前用户成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "bio": user.bio,
                "role": user.role,
                "status": user.status,
            },
        }
    ), 200



#修改个人资料
@app.patch("/api/auth/me")
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"message": "用户不存在"}), 404

    data = request.get_json(silent=True) or {}

    if "avatar_url" in data:
        user.avatar_url = (data.get("avatar_url") or "").strip()

    if "bio" in data:
        bio = (data.get("bio") or "").strip()

        if len(bio) > 500:
            return jsonify({"message": "个人简介不能超过500个字符"}), 400

        user.bio = bio

    db.session.commit()

    return jsonify({
        "message": "个人资料修改成功",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "bio": user.bio
        }
    }), 200




@app.get("/api/categories")
def get_categories():
    categories = Category.query.filter_by(status="active").order_by(Category.sort_order.asc()).all()

    data = []

    for category in categories:
        data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "sort_order": category.sort_order
        })

    return jsonify({
        "message": "分类查询成功",
        "data": data
    }), 200





@app.post("/api/posts")
@jwt_required()
def create_post():
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    category_id = data.get("category_id")

    if not title or not content or not category_id:
        return jsonify({"message": "标题、正文和分类不能为空"}), 400

    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None or user.status != "active":
        return jsonify({"message": "当前用户不可用"}), 403

    category = db.session.get(Category, category_id)

    if category is None or category.status != "active":
        return jsonify({"message": "所选分类不存在或已停用"}), 400

    post = Post(
        title=title,
        content=content,
        user_id=user.id,
        category_id=category.id
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({
        "message": "帖子发布成功",
        "data": {
            "id": post.id
        }
    }), 201




#帖子列表接口
@app.get("/api/posts")
def get_posts():
    page = max(request.args.get("page", 1, type=int), 1)

    per_page = request.args.get("per_page", 10, type=int)
    per_page = max(1, min(per_page, 50))

    #标题搜索
    keyword = (request.args.get("keyword") or "").strip()

    #按板块筛选
    category_id = request.args.get("category_id", type=int)

    query = Post.query.filter_by(status="published")

    if keyword:
        query = query.filter(
            or_(
                Post.title.contains(keyword),
                Post.content.contains(keyword)
            )
        )

    if category_id is not None:
        query = query.filter_by(category_id=category_id)

    pagination = query.order_by(
        Post.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    posts = pagination.items

    data = []

    for post in posts:
        data.append({
            "id": post.id,
            "title": post.title,
            "author": {
                "id": post.author.id,
                "username": post.author.username
            },
            "category": {
                "id": post.category.id,
                "name": post.category.name
            }
        })

    return jsonify({
        "message": "帖子列表获取成功",
        "data": data,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200





#单篇帖子详情接口
@app.get("/api/posts/<int:post_id>")
def get_post(post_id):
    post = db.session.get(Post, post_id)

    if post is None or post.status != "published":
        return jsonify({"message": "帖子不存在"}), 404

    post.view_count += 1      #记录浏览次数增长
    db.session.commit()

    return jsonify({
        "message": "帖子详情获取成功",
        "data": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "view_count": post.view_count,
            "like_count": PostLike.query.filter_by(
                post_id=post.id
            ).count(),
            "author": {
                "id": post.author.id,
                "username": post.author.username
            },
            "category": {
                "id": post.category.id,
                "name": post.category.name
            },
            "created_at": post.created_at.isoformat()
        }
    }), 200







#发表评论
@app.post("/api/posts/<int:post_id>/comments")
@jwt_required()
def create_comment(post_id):
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()

    if not content:
        return jsonify({"message": "评论内容不能为空"}), 400

    post = db.session.get(Post, post_id)

    if post is None or post.status != "published":
        return jsonify({"message": "帖子不存在"}), 404

    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None or user.status != "active":
        return jsonify({"message": "当前用户不可用"}), 403

    comment = Comment(
        content=content,
        user_id=user.id,
        post_id=post.id
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "message": "评论发表成功",
        "data": {
            "id": comment.id
        }
    }), 201





#获取评论
@app.get("/api/posts/<int:post_id>/comments")
def get_comments(post_id):
    post = db.session.get(Post, post_id)

    if post is None or post.status != "published":
        return jsonify({"message": "帖子不存在"}), 404

    comments = Comment.query.filter_by(      #查询 post_id 等于2的评论
        post_id=post.id,
        status="published"
    ).order_by(Comment.created_at.asc()).all()

    data = []

    for comment in comments:
        data.append({
            "id": comment.id,
            "content": comment.content,
            "author": {
                "id": comment.author.id,
                "username": comment.author.username
            },
            "created_at": comment.created_at.isoformat()
        })

    return jsonify({
        "message": "评论列表获取成功",
        "data": data
    }), 200






@app.post("/api/posts/<int:post_id>/likes")
@jwt_required()
def like_post(post_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None or user.status != "active":
        return jsonify({"message": "当前用户不可用"}), 403

    post = db.session.get(Post, post_id)

    if post is None or post.status != "published":
        return jsonify({"message": "帖子不存在"}), 404

    existing_like = PostLike.query.filter_by(
        user_id=user.id,
        post_id=post.id
    ).first()

    if existing_like is not None:
        return jsonify({"message": "你已经点赞过这篇帖子"}), 409

    post_like = PostLike(
        user_id=user.id,
        post_id=post.id
    )

    db.session.add(post_like)
    db.session.commit()

    return jsonify({
        "message": "点赞成功"
    }), 201







@app.delete("/api/posts/<int:post_id>/likes")
@jwt_required()
def unlike_post(post_id):
    user_id = int(get_jwt_identity())

    post_like = PostLike.query.filter_by(
        user_id=user_id,
        post_id=post_id
    ).first()

    if post_like is None:
        return jsonify({"message": "你还没有点赞这篇帖子"}), 404

    db.session.delete(post_like)
    db.session.commit()

    return jsonify({
        "message": "取消点赞成功"
    }), 200






#添加收藏接口
@app.post("/api/posts/<int:post_id>/favorites")
@jwt_required()
def favorite_post(post_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None or user.status != "active":
        return jsonify({"message": "当前用户不可用"}), 403

    post = db.session.get(Post, post_id)

    if post is None or post.status != "published":
        return jsonify({"message": "帖子不存在"}), 404

    existing_favorite = PostFavorite.query.filter_by(
        user_id=user.id,
        post_id=post.id
    ).first()

    if existing_favorite is not None:
        return jsonify({"message": "你已经收藏过这篇帖子"}), 409

    favorite = PostFavorite(
        user_id=user.id,
        post_id=post.id
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({
        "message": "收藏成功"
    }), 201







#取消收藏接口
@app.delete("/api/posts/<int:post_id>/favorites")
@jwt_required()
def unfavorite_post(post_id):
    user_id = int(get_jwt_identity())

    favorite = PostFavorite.query.filter_by(
        user_id=user_id,
        post_id=post_id
    ).first()

    if favorite is None:
        return jsonify({"message": "你还没有收藏这篇帖子"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({
        "message": "取消收藏成功"
    }), 200








#我的收藏列表
@app.get("/api/users/me/favorites")
@jwt_required()
def get_my_favorites():
    user_id = int(get_jwt_identity())

    favorites = PostFavorite.query.filter_by(
        user_id=user_id
    ).order_by(PostFavorite.created_at.desc()).all()

    data = []

    for favorite in favorites:
        post = favorite.post          #由relationship简化来的，因为配置了post = db.relationship("Post", backref="favorites")，所以可以直接用

        if post.status != "published":
            continue

        data.append({
            "id": favorite.id,
            "favorited_at": favorite.created_at.isoformat(),
            "post": {
                "id": post.id,
                "title": post.title
            }
        })

    return jsonify({
        "message": "收藏列表获取成功",
        "data": data
    }), 200






#编辑自己的帖子
@app.patch("/api/posts/<int:post_id>")           #patch表示部分修改帖子
@jwt_required()
def update_post(post_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None or user.status != "active":
        return jsonify({"message": "当前用户不可用"}), 403

    post = db.session.get(Post, post_id)

    if post is None or post.status == "deleted":
        return jsonify({"message": "帖子不存在"}), 404

    if post.user_id != user.id and user.role != "admin":
        return jsonify({"message": "你无权编辑这篇帖子"}), 403

    data = request.get_json(silent=True) or {}

    title = data.get("title")
    content = data.get("content")
    category_id = data.get("category_id")

    if title is None and content is None and category_id is None:
        return jsonify({"message": "没有提供需要修改的内容"}), 400

    if title is not None:
        if not isinstance(title, str):
            return jsonify({"message": "标题必须是字符串"}), 400

        title = title.strip()

        if not title or len(title) > 200:
            return jsonify({"message": "标题不能为空且不能超过200个字符"}), 400

        post.title = title

    if content is not None:
        if not isinstance(content, str):
            return jsonify({"message": "正文必须是字符串"}), 400

        content = content.strip()

        if not content:
            return jsonify({"message": "正文不能为空"}), 400

        post.content = content

    if category_id is not None:
        category = db.session.get(Category, category_id)

        if category is None or category.status != "active":
            return jsonify({"message": "所选分类不存在或已停用"}), 400

        post.category_id = category.id

    db.session.commit()

    return jsonify({
        "message": "帖子修改成功",
        "data": {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "category_id": post.category_id
        }
    }), 200









#删除帖子
@app.delete("/api/posts/<int:post_id>")
@jwt_required()
def delete_post(post_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None or user.status != "active":
        return jsonify({"message": "当前用户不可用"}), 403

    post = db.session.get(Post, post_id)

    if post is None or post.status == "deleted":
        return jsonify({"message": "帖子不存在"}), 404

    if post.user_id != user.id and user.role != "admin":
        return jsonify({"message": "你无权删除这篇帖子"}), 403

    post.status = "deleted"         #逻辑删除
    db.session.commit()

    return jsonify({
        "message": "帖子删除成功"
    }), 200









#编辑评论
@app.patch("/api/comments/<int:comment_id>")
@jwt_required()
def update_comment(comment_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    comment = db.session.get(Comment, comment_id)

    if user is None or user.status != "active":
        return jsonify({"message": "当前用户不可用"}), 403

    if comment is None or comment.status == "deleted":
        return jsonify({"message": "评论不存在"}), 404

    if comment.user_id != user.id and user.role != "admin":
        return jsonify({"message": "你无权编辑这条评论"}), 403

    data = request.get_json(silent=True) or {}
    content = data.get("content")

    if not isinstance(content, str) or not content.strip():
        return jsonify({"message": "评论内容不能为空"}), 400

    comment.content = content.strip()
    db.session.commit()

    return jsonify({
        "message": "评论修改成功",
        "data": {
            "id": comment.id,
            "content": comment.content
        }
    }), 200






#删除评论
@app.delete("/api/comments/<int:comment_id>")
@jwt_required()
def delete_comment(comment_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    comment = db.session.get(Comment, comment_id)

    if user is None or user.status != "active":
        return jsonify({"message": "当前用户不可用"}), 403

    if comment is None or comment.status == "deleted":
        return jsonify({"message": "评论不存在"}), 404

    if comment.user_id != user.id and user.role != "admin":
        return jsonify({"message": "你无权删除这条评论"}), 403

    comment.status = "deleted"
    db.session.commit()

    return jsonify({
        "message": "评论删除成功"
    }), 200








#查看我发布的帖子
@app.get("/api/users/me/posts")
@jwt_required()
def get_my_posts():
    user_id = int(get_jwt_identity())

    posts = Post.query.filter(
        Post.user_id == user_id,
        Post.status != "deleted"
    ).order_by(
        Post.created_at.desc()
    ).all()

    data = []

    for post in posts:
        data.append({
            "id": post.id,
            "title": post.title,
            "status": post.status,
            "view_count": post.view_count,
            "category": {
                "id": post.category.id,
                "name": post.category.name
            },
            "created_at": post.created_at.isoformat()
        })

    return jsonify({
        "message": "我的帖子获取成功",
        "data": data
    }), 200










#修改密码
@app.patch("/api/auth/password")
@jwt_required()
def update_password():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"message": "用户不存在"}), 404

    data = request.get_json(silent=True) or {}

    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    if not current_password or not new_password:
        return jsonify({
            "message": "当前密码和新密码不能为空"
        }), 400

    if not user.check_password(current_password):
        return jsonify({
            "message": "当前密码错误"
        }), 400

    if len(new_password) < 6:
        return jsonify({
            "message": "新密码不能少于6个字符"
        }), 400

    user.set_password(new_password)       #它不会把新密码原文存入数据库，而是调用：generate_password_hash(new_password)生成密码哈希，再保存到 password_hash 字段。
    db.session.commit()

    return jsonify({
        "message": "密码修改成功"
    }), 200










#管理员查看用户列表
@app.get("/api/admin/users")
@jwt_required()
def get_admin_users():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if current_user is None:
        return jsonify({"message": "用户不存在"}), 404

    if current_user.role != "admin":
        return jsonify({"message": "没有管理员权限"}), 403

    page = max(request.args.get("page", 1, type=int), 1)

    per_page = request.args.get("per_page", 10, type=int)
    per_page = max(1, min(per_page, 50))

    pagination = User.query.order_by(
        User.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    data = []

    for user in pagination.items:
        data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at.isoformat()
        })

    return jsonify({
        "message": "用户列表获取成功",
        "data": data,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200






#封禁或恢复用户
@app.patch("/api/admin/users/<int:user_id>/status")
@jwt_required()
def update_user_status(user_id):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if current_user is None:
        return jsonify({"message": "当前用户不存在"}), 404

    if current_user.role != "admin":
        return jsonify({"message": "没有管理员权限"}), 403

    target_user = db.session.get(User, user_id)

    if target_user is None:
        return jsonify({"message": "目标用户不存在"}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in ["active", "banned"]:
        return jsonify({
            "message": "用户状态只能是 active 或 banned"
        }), 400

    if target_user.id == current_user.id and new_status == "banned":
        return jsonify({
            "message": "管理员不能封禁自己"
        }), 400

    target_user.status = new_status
    db.session.commit()

    return jsonify({
        "message": "用户状态修改成功",
        "data": {
            "id": target_user.id,
            "username": target_user.username,
            "status": target_user.status
        }
    }), 200




# 管理员查看全部帖子
@app.get("/api/admin/posts")
@jwt_required()
def get_admin_posts():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if current_user is None:
        return jsonify({"message": "当前用户不存在"}), 404

    if current_user.role != "admin":
        return jsonify({"message": "没有管理员权限"}), 403

    page = max(request.args.get("page", 1, type=int), 1)

    per_page = request.args.get("per_page", 10, type=int)
    per_page = max(1, min(per_page, 50))

    pagination = Post.query.order_by(
        Post.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    data = []

    for post in pagination.items:
        data.append({
            "id": post.id,
            "title": post.title,
            "status": post.status,
            "author": {
                "id": post.author.id,
                "username": post.author.username
            },
            "category": {
                "id": post.category.id,
                "name": post.category.name
            },
            "created_at": post.created_at.isoformat()
        })

    return jsonify({
        "message": "管理员帖子列表获取成功",
        "data": data,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200






#管理员审核帖子状态
@app.patch("/api/admin/posts/<int:post_id>/status")
@jwt_required()
def update_post_status(post_id):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if current_user is None:
        return jsonify({"message": "当前用户不存在"}), 404

    if current_user.role != "admin":
        return jsonify({"message": "没有管理员权限"}), 403

    post = db.session.get(Post, post_id)

    if post is None:
        return jsonify({"message": "帖子不存在"}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    allowed_statuses = ["published", "hidden", "deleted"]

    if new_status not in allowed_statuses:
        return jsonify({
            "message": "帖子状态不正确"
        }), 400

    post.status = new_status
    db.session.commit()

    return jsonify({
        "message": "帖子状态修改成功",
        "data": {
            "id": post.id,
            "title": post.title,
            "status": post.status
        }
    }), 200





# 管理员查看全部评论
@app.get("/api/admin/comments")
@jwt_required()
def get_admin_comments():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if current_user is None:
        return jsonify({"message": "当前用户不存在"}), 404

    if current_user.role != "admin":
        return jsonify({"message": "没有管理员权限"}), 403

    page = max(request.args.get("page", 1, type=int), 1)

    per_page = request.args.get("per_page", 10, type=int)
    per_page = max(1, min(per_page, 50))

    pagination = Comment.query.order_by(
        Comment.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    data = []

    for comment in pagination.items:
        data.append({
            "id": comment.id,
            "content": comment.content,
            "status": comment.status,
            "author": {
                "id": comment.author.id,
                "username": comment.author.username
            },
            "post": {
                "id": comment.post.id,
                "title": comment.post.title
            },
            "created_at": comment.created_at.isoformat()
        })

    return jsonify({
        "message": "管理员评论列表获取成功",
        "data": data,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200



# 管理员隐藏或恢复评论
@app.patch("/api/admin/comments/<int:comment_id>/status")
@jwt_required()
def update_comment_status(comment_id):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if current_user is None:
        return jsonify({"message": "当前用户不存在"}), 404

    if current_user.role != "admin":
        return jsonify({"message": "没有管理员权限"}), 403

    comment = db.session.get(Comment, comment_id)

    if comment is None:
        return jsonify({"message": "评论不存在"}), 404

    if comment.status == "deleted":
        return jsonify({
            "message": "用户已删除的评论不能恢复"
        }), 400

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in ["published", "hidden"]:
        return jsonify({
            "message": "评论状态只能是 published 或 hidden"
        }), 400

    comment.status = new_status
    db.session.commit()

    return jsonify({
        "message": "评论状态修改成功",
        "data": {
            "id": comment.id,
            "status": comment.status
        }
    }), 200







# 管理员查看全部板块
@app.get("/api/admin/categories")
@jwt_required()
def get_admin_categories():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if current_user is None:
        return jsonify({"message": "当前用户不存在"}), 404

    if current_user.role != "admin":
        return jsonify({"message": "没有管理员权限"}), 403

    categories = Category.query.order_by(
        Category.sort_order.asc()
    ).all()

    data = []

    for category in categories:
        data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "sort_order": category.sort_order,
            "status": category.status
        })

    return jsonify({
        "message": "管理员板块列表获取成功",
        "data": data
    }), 200


# 管理员停用或恢复板块
@app.patch("/api/admin/categories/<int:category_id>/status")
@jwt_required()
def update_category_status(category_id):
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if current_user is None:
        return jsonify({"message": "当前用户不存在"}), 404

    if current_user.role != "admin":
        return jsonify({"message": "没有管理员权限"}), 403

    category = db.session.get(Category, category_id)

    if category is None:
        return jsonify({"message": "板块不存在"}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status not in ["active", "inactive"]:
        return jsonify({
            "message": "板块状态只能是 active 或 inactive"
        }), 400

    category.status = new_status
    db.session.commit()

    return jsonify({
        "message": "板块状态修改成功",
        "data": {
            "id": category.id,
            "name": category.name,
            "status": category.status
        }
    }), 200




# 管理员创建板块
@app.post("/api/admin/categories")
@jwt_required()
def create_admin_category():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if current_user is None:
        return jsonify({"message": "当前用户不存在"}), 404

    if current_user.role != "admin":
        return jsonify({"message": "没有管理员权限"}), 403

    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()
    sort_order = data.get("sort_order", 0)

    if not name:
        return jsonify({"message": "板块名称不能为空"}), 400

    if len(name) > 50:
        return jsonify({"message": "板块名称不能超过50个字符"}), 400

    try:
        sort_order = int(sort_order)
    except (TypeError, ValueError):
        return jsonify({"message": "排序必须是整数"}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"message": "板块名称已存在"}), 409

    category = Category(
        name=name,
        description=description or None,
        sort_order=sort_order
    )

    db.session.add(category)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "板块名称已存在"}), 409

    return jsonify({
        "message": "板块创建成功",
        "data": {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "sort_order": category.sort_order,
            "status": category.status
        }
    }), 201




if __name__ == "__main__":
    app.run(debug=True)