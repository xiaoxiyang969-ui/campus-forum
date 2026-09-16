<script setup>
import { onMounted, reactive, ref } from "vue"
import axios from "axios"
import {handleAuthError, token} from "../stores/auth"
import { useRouter } from "vue-router"

const user = ref(null)
const posts = ref([])
const favorites = ref([])
const message = ref("")
const loading = ref(true)
const router = useRouter()
const profileForm = reactive({
  avatar_url: "",
  bio: ""
})



//获取“当前用户资料”
async function loadProfile() {
  if (!token.value) {
    message.value = "请先登录"
    loading.value = false
    return
  }

  try {
    //获取一个用户对象，保存到：user.value
    const response = await axios.get(       //GET 一般不需要请求体
        "http://127.0.0.1:5000/api/auth/me",
        {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        }
    )
    user.value = response.data.data
    profileForm.avatar_url = user.value.avatar_url || ""
    profileForm.bio = user.value.bio || ""

    //获取当前用户发布的帖子数组，保存到：posts.value
    const postsResponse = await axios.get(
        "http://127.0.0.1:5000/api/users/me/posts",
        {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        }
    )
    posts.value = postsResponse.data.data


    //我的收藏
    const favoritesResponse = await axios.get(
        "http://127.0.0.1:5000/api/users/me/favorites",
        {
          headers: {
            Authorization: `Bearer ${token.value}`
          }
        }
    )

    favorites.value = favoritesResponse.data.data
  } catch (error) {
    if (handleAuthError(error)) {
      router.push({
        path: "/login",
        query: {
          reason: "expired"
        }
      })
      return               //身份错误已经处理完毕后，立即结束 catch，不会继续显示普通的“获取个人信息失败”。
    }
    message.value =
        error.response?.data?.message ||
        error.response?.data?.msg ||
        "获取个人信息失败"
  } finally {
    loading.value = false
  }
}







//删除帖子
async function deleteMyPost(postId) {
  const confirmed = window.confirm("确定要删除这篇帖子吗？")

  if (!confirmed) {
    return
  }

  try {
    await axios.delete(
      `http://127.0.0.1:5000/api/posts/${postId}`,
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    posts.value = posts.value.filter(        //filter() 会创建一个新数组，只保留 ID 不等于被删除 ID 的帖子，因此页面会立刻移除那篇帖子，不用刷新。
      post => post.id !== postId           //filter() 会把数组中的每篇帖子依次交给箭头函数。
    )
  } catch (error) {
    message.value =
      error.response?.data?.message ||
      error.response?.data?.msg ||
      "删除帖子失败"
  }
}



//修改函数
async function updateProfile() {
  message.value = ""

  try {
    const response = await axios.patch(
      "http://127.0.0.1:5000/api/auth/me",
      profileForm,
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )
//保留原来的用户资料+用后端返回的新资料覆盖对应字段
    user.value = {
      ...user.value,
      ...response.data.data
    }

    message.value = response.data.message
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

    message.value =
      error.response?.data?.message ||
      error.response?.data?.msg ||
      "修改个人资料失败"
  }
}

onMounted(loadProfile)        //等这个页面组件在浏览器里渲染显示出来之后，立刻去执行 loadProfile 这个函数
</script>


<template>
  <main class="profile-page">
    <h1>个人中心</h1>

    <p v-if="loading">
      正在加载个人信息……
    </p>

    <p v-if="!loading && message">
      {{ message }}
    </p>

    <section v-if="!loading && user" class="profile-card">
      <h2>{{ user.username }}</h2>

      <p>邮箱：{{ user.email }}</p>
      <p>角色：{{ user.role }}</p>
      <p>状态：{{ user.status }}</p>
      <p>个人简介：{{ user.bio || "暂未填写" }}</p>


      <!--编辑表单-->
      <form
          class="profile-form"
          @submit.prevent="updateProfile"
      >
        <label>
          头像网址
          <input
              v-model="profileForm.avatar_url"
              type="url"
              placeholder="https://example.com/avatar.jpg"
          >
        </label>

        <label>
          个人简介
          <textarea
              v-model="profileForm.bio"
              rows="4"
              maxlength="500"
          ></textarea>
        </label>

        <button type="submit">
          保存个人资料
        </button>
      </form>


      <!--我的帖子-->
      <section class="my-posts">
        <h2>我发布的帖子</h2>

        <p v-if="posts.length === 0">
          暂未发布帖子
        </p>

        <div v-else>
          <article
              v-for="post in posts"
              :key="post.id"
              class="my-post-card"
          >
            <h3>
              <RouterLink :to="`/posts/${post.id}`">
                {{ post.title }}
              </RouterLink>
            </h3>

            <p>板块：{{ post.category.name }}</p>
            <p>状态：{{ post.status }}</p>
            <p>浏览次数：{{ post.view_count }}</p>

            <RouterLink
                class="edit-link"
                :to="`/posts/${post.id}/edit`"
            >
              编辑
            </RouterLink>
            <button
                type="button"
                class="delete-button"
                @click="deleteMyPost(post.id)"
            >
              删除
            </button>
          </article>
        </div>
      </section>


      <!--我的收藏-->
      <section class="my-favorites">
        <h2>我的收藏</h2>

        <p v-if="favorites.length === 0">
          暂无收藏
        </p>

        <div v-else>
          <article
              v-for="favorite in favorites"
              :key="favorite.id"
              class="favorite-card"
          >
            <RouterLink :to="`/posts/${favorite.post.id}`">
              {{ favorite.post.title }}
            </RouterLink>
          </article>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.profile-page {
  max-width: 900px;
  margin: 40px auto;
  padding: 24px;
}

.profile-card {
  padding: 24px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 10px;
}

.my-posts,
.my-favorites {
  margin-top: 32px;
}

.my-post-card,
.favorite-card {
  margin-top: 12px;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.my-post-card h3 {
  margin-top: 0;
}

.my-post-card a,
.favorite-card a {
  color: #2563eb;
  text-decoration: none;
}

.my-post-card a:hover,
.favorite-card a:hover {
  text-decoration: underline;
}

.delete-button {
  padding: 8px 16px;
  color: white;
  background: #dc2626;
  border: 0;
  border-radius: 6px;
  cursor: pointer;
}

.delete-button:hover {
  background: #b91c1c;
}

.edit-link {
  margin-right: 12px;
}

.delete-button {
  color: #f5f7fa;
  cursor: pointer;
}
</style>