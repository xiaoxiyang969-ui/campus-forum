<script setup>
import { reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import axios from "axios"
import { saveRole, saveToken } from "../stores/auth"

const router = useRouter()
const route = useRoute()

const form = reactive({
  username: "",
  password: ""
})

//它的作用是：检查网址参数，如果原因是过期，就设置提示文字；否则提示为空
const message = ref(
  route.query.reason === "expired"            //route.query  表示读取当前网址中 ? 后面的查询参数
    ? "登录已过期，请重新登录"                         //判断条件 ? 是的时候用这个 : 否的时候用这个
    : ""
)

async function handleSubmit() {
  message.value = ""

  try {
    const response = await axios.post(
      "http://127.0.0.1:5000/api/auth/login",
      form
    )

    const token = response.data.data.access_token
    saveToken(token)
    saveRole(response.data.data.role)

    message.value = response.data.message

    router.push("/")       //在JavaScript中跳转到："/",即首页
  } catch (error) {
    message.value =
      error.response?.data?.message || "登录请求失败"
  }
}
</script>

<template>
  <main class="login-page">
    <form class="login-form" @submit.prevent="handleSubmit">
      <h2>用户登录</h2>

      <label for="username">用户名</label>
      <input
        id="username"
        v-model="form.username"
        type="text"
        required
      >

      <label for="password">密码</label>
      <input
        id="password"
        v-model="form.password"
        type="password"
        required
      >

      <button type="submit">登录</button>
      <p v-if="message" class="message">
  {{ message }}
</p>
    </form>
  </main>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.login-form {
  display: flex;
  width: 360px;
  flex-direction: column;
  gap: 12px;
  padding: 24px;
  background-color: white;
  border-radius: 8px;
}

.login-form input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.login-form button {
  margin-top: 12px;
  padding: 10px;
  color: white;
  cursor: pointer;
  border: 0;
  border-radius: 4px;
  background-color: #409eff;
}

.message {
  margin: 0;
  text-align: center;
}
</style>