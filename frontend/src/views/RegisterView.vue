<script setup>
import { reactive, ref } from "vue"
import axios from "axios"
import { useRouter } from "vue-router"

const form = reactive({
  username: "",
  email: "",
  password: ""
})

const message = ref("")//保存注册成功或失败的提示文字
const router = useRouter()       //获取 Vue Router 提供的“路由控制器”，并把它保存到变量 router 中
//useRoute()：读取当前网址的信息，例如帖子 ID。
//useRouter()：主动跳转到另一个网址。


//注册请求
async function handleSubmit() {
  message.value = ""

  try {
    const response = await axios.post(
      "https://campus-forum-production-2e9a.up.railway.app/api/auth/register",
      form
    )

    message.value = response.data.message
    router.push("/login")
  } catch (error) {
    message.value =
      error.response?.data?.message || "注册请求失败"
  }
}
</script>






<template>
  <main class="register-page">
    <h1>注册</h1>

    <form @submit.prevent="handleSubmit">
      <label>
        用户名
        <input
          v-model="form.username"
          type="text"
          required
        >
      </label>

      <label>
        邮箱
        <input
          v-model="form.email"
          type="email"
          required
        >
      </label>

      <label>
        密码
        <input
          v-model="form.password"
          type="password"
          required
        >
      </label>

      <button type="submit">注册</button>
    </form>

    <p v-if="message">{{ message }}</p>      <!--只有 message 有内容时才显示这个段落，然后用 {{ message }} 显示注册结果-->
  </main>
</template>

<style scoped>

</style>