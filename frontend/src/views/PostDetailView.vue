<script setup>
import { onMounted, ref } from "vue"
import axios from "axios"
import { useRoute, useRouter } from "vue-router"   //useRouter()用于主动跳转到另一个页面    useRoute()用于读取当前所在页面的网址信息
import { handleAuthError } from "../stores/auth"

const route = useRoute()
const router = useRouter()
const postId = route.params.id     //params 是 parameters 的缩写，意思是“参数”,在Vue Router中，params 专门保存网址路径中的动态参数。
const post = ref(null)
const comments = ref([])
const newComment = ref("")
const errorMessage = ref("")


async function loadPost() {
  try {
    //获取帖子详情
    const response = await axios.get(
        `http://127.0.0.1:5000/api/posts/${postId}`
    )
    post.value = response.data.data

    //获取评论数据
    const commentsResponse = await axios.get(
        `http://127.0.0.1:5000/api/posts/${postId}/comments`
    )
    comments.value = commentsResponse.data.data

  } catch (error) {
    console.error("获取帖子详情失败", error)

    errorMessage.value =
        error.response?.data?.message || "获取帖子详情失败"
  }
}






//发表评论
async function submitComment() {
  //检查是否登录
  const token = localStorage.getItem("access_token")

  if (!token) {
    alert("请先登录")
    return
  }

  try {
  await axios.post(
    `http://127.0.0.1:5000/api/posts/${postId}/comments`,
    {
      content: newComment.value
    },
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  )

  newComment.value = ""

  const commentsResponse = await axios.get(
    `http://127.0.0.1:5000/api/posts/${postId}/comments`
  )

  comments.value = commentsResponse.data.data
} catch (error) {
    if (handleAuthError(error)) {
  router.push({
  path: "/login",
  query: {
    reason: "expired"
  }
})
  return
}
  alert(
    error.response?.data?.message || "发表评论失败"
  )
}
}





//点赞
async function likePost() {
  const token = localStorage.getItem("access_token")

  if (!token) {
    alert("请先登录")
    return
  }

  try {
    await axios.post(
      `http://127.0.0.1:5000/api/posts/${postId}/likes`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    post.value.like_count += 1
  } catch (error) {
    if (handleAuthError(error)) {
  router.push({
  path: "/login",
  query: {
    reason: "expired"
  }
})
  return
}
    alert(
      error.response?.data?.message || "点赞失败"
    )
  }
}




//取消点赞
async function unlikePost() {
  const token = localStorage.getItem("access_token")

  if (!token) {
    alert("请先登录")
    return
  }

  try {
    await axios.delete(
      `http://127.0.0.1:5000/api/posts/${postId}/likes`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    post.value.like_count = Math.max(
      0,
      post.value.like_count - 1
    )
  } catch (error) {
    if (handleAuthError(error)) {
  router.push({
  path: "/login",
  query: {
    reason: "expired"
  }
})
  return
}
    alert(         //alert() 是浏览器内置的弹窗函数。
      error.response?.data?.message || "取消点赞失败"
    )
  }
}




//收藏帖子
async function favoritePost() {
  const token = localStorage.getItem("access_token")

  if (!token) {
    alert("请先登录")
    return
  }

  try {
    await axios.post(
      `http://127.0.0.1:5000/api/posts/${postId}/favorites`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    alert("收藏成功")
  } catch (error) {
    if (handleAuthError(error)) {
  router.push({
  path: "/login",
  query: {
    reason: "expired"
  }
})
  return
}
    alert(
      error.response?.data?.message || "收藏失败"
    )
  }
}





//取消收藏
async function unfavoritePost() {
  const token = localStorage.getItem("access_token")

  if (!token) {
    alert("请先登录")
    return
  }

  try {
    await axios.delete(
      `http://127.0.0.1:5000/api/posts/${postId}/favorites`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    alert("取消收藏成功")
  } catch (error) {
    if (handleAuthError(error)) {
      router.push({
        path: "/login",
        query: {
          reason: "expired"        ///login?reason=expired    问号后为附加信息，最后仍跳转/login
        }
      })
      return
}
    alert(
      error.response?.data?.message || "取消收藏失败"
    )
  }
}

onMounted(loadPost)      //当当前Vue页面组件被加载到浏览器中以后，自动执行 loadPost 函数
</script>














<template>
  <main class="post-detail">
    <p v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </p>
    <article v-else-if="post">
  <h1>{{ post.title }}</h1>

  <p>
    作者：{{ post.author.username }}
  </p>

  <p>
    板块：{{ post.category.name }}
  </p>

  <div class="content">
    {{ post.content }}
  </div>

  <p>
    浏览次数：{{ post.view_count }}
  </p>

  <p>
    点赞数量：{{ post.like_count }}
  </p>
      <button type="button" @click="likePost">
  点赞
</button>
      <button type="button" @click="favoritePost">
  收藏
</button>
      <!--创建一个不会提交表单的普通按钮,按钮被点击时，执行前面定义的：unlikePost()取消点赞代码-->
      <button type="button" @click="unlikePost">
  取消点赞
</button>
      <button type="button" @click="unfavoritePost">
  取消收藏
</button>

  <section class="comments">
  <h2>评论</h2>

    <form class="comment-form" @submit.prevent="submitComment">
  <textarea
    v-model="newComment"
    placeholder="请输入评论内容"
    rows="4"
    required
  ></textarea>

  <button type="submit">
    发表评论
  </button>
</form>

  <p v-if="comments.length === 0">
    暂无评论
  </p>

  <div v-else>
    <article
      v-for="comment in comments"
      :key="comment.id"
      class="comment-card"
    >
      <p>{{ comment.content }}</p>
      <small>
        {{ comment.author.username }}     <!--浏览器默认会把 <small> 里面的文字显示得比普通文字小一些-->
      </small>
    </article>
  </div>
</section>

</article>

<p v-else>
  正在加载帖子……
</p>
  </main>
</template>









<style scoped>
.post-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.content {
  margin: 30px 0;
  line-height: 1.8;     /*增加正文行间距*/
  white-space: pre-wrap;       /*保留源代码中的空格和换行，但同时允许文本自动换行*/
}

.error-message {
  color: #f56c6c;
  text-align: center;
}

.comments {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.comment-card {
  margin-bottom: 12px;
  padding: 16px;
  background-color: white;
  border-radius: 6px;
}

.comment-card p {
  margin-top: 0;
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.comment-form textarea {
  padding: 12px;
  resize: vertical;     /*表示用户可以上下拖动改变文本框高度，但不能左右拉伸。*/
}

.comment-form button {
  align-self: flex-end;      /*让发表按钮位于表单右侧*/
  padding: 8px 16px;
  cursor: pointer;
}
</style>