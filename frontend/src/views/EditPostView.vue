<script setup>
import { onMounted, reactive, ref } from "vue"
import axios from "axios"
import { useRoute, useRouter } from "vue-router"
import {
  handleAuthError,
  token
} from "../stores/auth"

const route = useRoute()
const router = useRouter()
const postId = route.params.id

const form = reactive({
  title: "",
  content: "",
  category_id: null
})

const categories = ref([])
const message = ref("")
const loading = ref(true)




//自动加载原帖内容和板块列表
async function loadEditData() {
  if (!token.value) {
    message.value = "请先登录"
    loading.value = false
    return
  }

  try {
    const postResponse = await axios.get(
      `https://campus-forum-production-2e9a.up.railway.app/api/posts/${postId}`
    )

    const post = postResponse.data.data

    form.title = post.title
    form.content = post.content
    form.category_id = post.category.id

    const categoriesResponse = await axios.get(
      "https://campus-forum-production-2e9a.up.railway.app/api/categories"
    )

    categories.value = categoriesResponse.data.data
  } catch (error) {
    message.value =
      error.response?.data?.message ||
      error.response?.data?.msg ||
      "获取帖子信息失败"
  } finally {
    loading.value = false
  }
}



//提交修改
async function handleSubmit() {
  if (!token.value) {
    message.value = "请先登录"
    return
  }

  message.value = ""

  try {
    const response = await axios.patch(
      `https://campus-forum-production-2e9a.up.railway.app/api/posts/${postId}`,
      form,
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    message.value = response.data.message
    router.push(`/posts/${postId}`)
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
      "修改帖子失败"
  }
}

onMounted(loadEditData)
</script>





<template>
  <main class="edit-post-page">
    <h1>编辑帖子</h1>

    <p v-if="loading">
      正在加载帖子……
    </p>

    <div v-else>
      <p v-if="message">
        {{ message }}
      </p>

      <form @submit.prevent="handleSubmit">
        <label>
          标题
          <input
            v-model="form.title"
            type="text"
            required
          > <!--required 是 HTML 表单验证属性，意思是“必填，不能为空”-->
        </label>

        <label>
          正文
          <textarea
            v-model="form.content"
            rows="10"
            required
          ></textarea>
        </label>

        <label>
          板块
          <select
            v-model.number="form.category_id"
            required
          >
            <option
              v-for="category in categories"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
        </label>

        <div class="form-actions">
          <button type="submit">
            保存修改
          </button>

          <RouterLink :to="`/posts/${postId}`">
            取消
          </RouterLink>
        </div>
      </form>
    </div>
  </main>
</template>

<style scoped>
.edit-post-page {
  max-width: 760px;
  margin: 40px auto;
  padding: 24px;
}

.edit-post-page form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.edit-post-page label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 600;
}

.edit-post-page input,
.edit-post-page textarea,
.edit-post-page select {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  font: inherit;
}

.edit-post-page textarea {
  min-height: 220px;
  resize: vertical;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.form-actions button {
  padding: 10px 24px;
  cursor: pointer;
}

.form-actions a {
  color: #555;
}
</style>