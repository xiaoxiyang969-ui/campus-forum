<script setup>
import { onMounted, reactive, ref } from "vue"
import axios from "axios"
import { useRouter } from "vue-router"
import {
  handleAuthError,
  token
} from "../stores/auth"

const form = reactive({
  title: "",
  content: "",
  category_id: null
})

const message = ref("")
const categories = ref([])
const router = useRouter()





async function loadCategories() {
  try {
    const response = await axios.get(
      "http://127.0.0.1:5000/api/categories"
    )

    categories.value = response.data.data

    if (categories.value.length > 0) {
      form.category_id = categories.value[0].id
    }
  } catch (error) {
    message.value =
      error.response?.data?.message || "获取板块列表失败"
  }
}




//发帖函数
async function handleSubmit() {
  message.value = ""

  if (!token.value) {        //这里必须写token.value，因为现在位于 JavaScript 的 <script setup> 中。只有在 <template> 中，Vue 才会帮我们自动省略 .value。
    message.value = "请先登录"
    return
  }

  try {
    const response = await axios.post(
      "http://127.0.0.1:5000/api/posts",
      form,
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    message.value = response.data.message
    router.push("/")
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
        error.response?.data?.message || "发布帖子失败"
  }
}

onMounted(loadCategories)
</script>


<template>
  <main class="create-post-page">
    <h1>发布帖子</h1>

    <form @submit.prevent="handleSubmit">
      <label>
        标题
        <input
            v-model="form.title"
            type="text"
            required
        >
      </label>

      <label>
        正文
        <!--输入框默认显示大约十行的高度-->
        <!--<textarea>（多行文本输入框）-->
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

      <button type="submit">发布</button>
    </form>

    <p v-if="message">{{ message }}</p>
  </main>
</template>
<style scoped>
.create-post-page {
  max-width: 760px;
  margin: 40px auto;
  padding: 24px;
}


.create-post-page form {
  display: flex;          /*开启弹性布局*/
  flex-direction: column;      /*改变排列方向为垂直*/
  gap: 20px;
}

.create-post-page label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 600;
}

/*组合选择器*/
.create-post-page input,
.create-post-page textarea,
.create-post-page select {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  font: inherit;
}

/*单独选择器*/
.create-post-page textarea {
  min-height: 220px;
  resize: vertical;       /*只能上下拖拽*/
}

.create-post-page button {
  align-self: flex-start;
  padding: 10px 24px;
  cursor: pointer;
}
</style>