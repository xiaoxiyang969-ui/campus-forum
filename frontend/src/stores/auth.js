//此文件专门负责与登录身份有关的数据和操作
import { ref } from "vue"

//export：允许 LoginView.vue、App.vue 等其他文件共同使用这个 token。
export const token = ref(
  localStorage.getItem("access_token")
)

//登录成功后，同时把 JWT 保存到两个地方
export function saveToken(value) {
  token.value = value
  localStorage.setItem("access_token", value)
}

export function saveRole(value) {
  role.value = value
  localStorage.setItem("user_role", value)
}

//退出登录
export function clearToken() {
  token.value = null
  localStorage.removeItem("access_token")
  role.value = null
  localStorage.removeItem("user_role")
}

//处理 Token 失效后的自动退出
export function handleAuthError(error) {
  if (error.response?.status !== 401) {         //如果不是身份验证错误，就不处理，返回 false
    return false
  }

  //如果状态码正好是 401,就清除失效 Token，并告诉调用它的页面：“这确实是登录身份错误”
  clearToken()
  return true
}

export const role = ref(
  localStorage.getItem("user_role")
)