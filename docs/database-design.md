# 校园论坛数据库设计

## 核心数据对象

- User：用户
- Category：论坛板块
- Post：帖子
- Comment：评论
- PostLike：帖子点赞记录
- Favorite：帖子收藏记录

## 数据关系

- 一个用户可以发布多篇帖子
- 一篇帖子只属于一个用户
- 一个板块可以包含多篇帖子
- 一篇帖子只属于一个板块
- 一个用户可以发表多条评论
- 一篇帖子可以包含多条评论
- 用户和帖子通过 PostLike 建立点赞关系
- 用户和帖子通过 Favorite 建立收藏关系

## 关系表示

- User 1:N Post
- Category 1:N Post
- User 1:N Comment
- Post 1:N Comment
- User N:N Post，通过 PostLike 实现
- User N:N Post，通过 Favorite 实现

## users 用户表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | 主键、自增、非空 | 用户唯一编号 |
| username | VARCHAR(50) | 唯一、非空 | 用户名 |
| email | VARCHAR(120) | 唯一、非空 | 邮箱 |
| password_hash | VARCHAR(255) | 非空 | 加密后的密码 |
| avatar_url | VARCHAR(255) | 可空 | 头像地址 |
| bio | VARCHAR(255) | 可空 | 个人简介 |
| role | VARCHAR(20) | 默认 user、非空 | user 或 admin |
| status | VARCHAR(20) | 默认 active、非空 | active 或 disabled |
| created_at | DATETIME | 非空 | 注册时间 |
| updated_at | DATETIME | 非空 | 资料最后更新时间 |

## categories 板块表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | 主键、自增、非空 | 板块唯一编号 |
| name | VARCHAR(50) | 唯一、非空 | 板块名称 |
| description | VARCHAR(255) | 可空 | 板块介绍 |
| sort_order | INT | 默认 0、非空 | 展示顺序 |
| is_enabled | BOOLEAN | 默认 true、非空 | 是否启用 |
| created_at | DATETIME | 非空 | 创建时间 |
| updated_at | DATETIME | 非空 | 修改时间 |

## posts 帖子表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | 主键、自增、非空 | 帖子唯一编号 |
| user_id | BIGINT | 外键、非空 | 引用 users.id |
| category_id | BIGINT | 外键、非空 | 引用 categories.id |
| title | VARCHAR(200) | 非空 | 帖子标题 |
| content | TEXT | 非空 | 帖子正文 |
| status | VARCHAR(20) | 默认 published、非空 | 帖子状态 |
| view_count | INT | 默认 0、非空 | 浏览次数 |
| created_at | DATETIME | 非空 | 发布时间 |
| updated_at | DATETIME | 非空 | 修改时间 |

## 外键关系

- posts.user_id 引用 users.id
- posts.category_id 引用 categories.id

## comments 评论表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | 主键、自增、非空 | 评论唯一编号 |
| user_id | BIGINT | 外键、非空 | 引用 users.id |
| post_id | BIGINT | 外键、非空 | 引用 posts.id |
| content | TEXT | 非空 | 评论内容 |
| status | VARCHAR(20) | 默认 published、非空 | 评论状态 |
| created_at | DATETIME | 非空 | 发表时间 |
| updated_at | DATETIME | 非空 | 修改时间 |

## post_likes 点赞表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | 主键、自增、非空 | 点赞记录编号 |
| user_id | BIGINT | 外键、非空 | 引用 users.id |
| post_id | BIGINT | 外键、非空 | 引用 posts.id |
| created_at | DATETIME | 非空 | 点赞时间 |

联合唯一约束：user_id + post_id。

## favorites 收藏表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | 主键、自增、非空 | 收藏记录编号 |
| user_id | BIGINT | 外键、非空 | 引用 users.id |
| post_id | BIGINT | 外键、非空 | 引用 posts.id |
| created_at | DATETIME | 非空 | 收藏时间 |

联合唯一约束：user_id + post_id。

## 补充外键关系

- comments.user_id 引用 users.id
- comments.post_id 引用 posts.id
- post_likes.user_id 引用 users.id
- post_likes.post_id 引用 posts.id
- favorites.user_id 引用 users.id
- favorites.post_id 引用 posts.id

## 索引设计

- users.username：唯一索引
- users.email：唯一索引
- posts(category_id, created_at)：按板块查询最新帖子
- posts(user_id, created_at)：查询用户发布的帖子
- comments(post_id, created_at)：加载帖子的评论
- post_likes(user_id, post_id)：联合唯一索引
- favorites(user_id, post_id)：联合唯一索引

索引只添加在经常用于查询、排序、关联和唯一判断的字段上。

## 删除策略

- 用户：软删除，将 status 改为 disabled
- 板块：软删除，将 is_enabled 改为 false
- 帖子：软删除，将 status 改为 deleted 或 hidden
- 评论：软删除，将 status 改为 deleted 或 hidden
- 点赞：硬删除对应记录
- 收藏：硬删除对应记录