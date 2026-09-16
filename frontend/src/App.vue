<script setup>
import {useRouter} from "vue-router"
import { clearToken, role, token } from "./stores/auth"

const router = useRouter()

//退出函数
function logout() {
  clearToken()     //从浏览器本地存储中删除JWT
  router.push("/login")     //退出成功后跳转到登录页面
}
</script>


<template>
  <div class="app">
    <header class="header">
      <h1>校园论坛</h1>

      <nav class="nav">
        <RouterLink to="/">首页</RouterLink>          <!--<RouterLink>：创建一个可以跳转的链接-->
        <!--把两个链接组合起来，一起受到 v-if 控制,<template> 在这里是一个逻辑容器，不会在最终网页中生成额外的可见标签-->
        <template v-if="!token">
          <RouterLink to="/login">登录</RouterLink>
          <RouterLink to="/register">注册</RouterLink>
        </template>

        <template v-else>
          <RouterLink to="/profile">个人中心</RouterLink>
          <RouterLink to="/posts/create">发布帖子</RouterLink>
          <RouterLink
              v-if="role === 'admin'"
              to="/admin"
          >
            管理员后台
          </RouterLink>

          <button type="button" @click="logout">
            退出登录
          </button>
        </template>
      </nav>
    </header>

    <RouterView/>
  </div>
</template>


<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  border-bottom: 1px solid #ddd;
}

.header h1 {
  margin: 0;
  font-size: 24px;
}

.header a {
  color: #333;
  text-decoration: none;
}

.nav {
  display: flex;
  gap: 20px;
}

.nav button {
  padding: 0;
  color: #333;
  cursor: pointer;
  border: 0;
  background: none;
}
</style>