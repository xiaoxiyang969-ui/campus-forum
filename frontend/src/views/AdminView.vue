<script setup>
import { onMounted, reactive, ref } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import { handleAuthError, token } from "../stores/auth"

const router = useRouter()

const users = ref([])
const loading = ref(true)
const message = ref("")
const posts = ref([])
const postsLoading = ref(true)
const postsMessage = ref("")
const comments = ref([])
const commentsLoading = ref(true)
const commentsMessage = ref("")
const categories = ref([])
const categoriesLoading = ref(true)
const categoriesMessage = ref("")
const categoryForm = reactive({
  name: "",
  description: "",
  sort_order: 0
})




async function loadUsers() {
  try {
    const response = await axios.get(
      "https://campus-forum-production-2e9a.up.railway.app/api/admin/users",
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    users.value = response.data.data
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
      error.response?.data?.message ||         //?.叫可选链，如果 error.response 不存在，普通写法：error.response.data.message会再次报错。而error.response?.data?.message发现某一层不存在时会安全地返回 undefined，不会让页面再次崩溃。
      error.response?.data?.msg ||
      "获取用户列表失败"
  } finally {
    loading.value = false
  }
}



//管理员帖子列表
async function loadPosts() {
  try {
    const response = await axios.get(
      "https://campus-forum-production-2e9a.up.railway.app/api/admin/posts",
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    posts.value = response.data.data
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

    postsMessage.value =
      error.response?.data?.message ||
      "获取帖子列表失败"
  } finally {
    postsLoading.value = false
  }
}




//加载评论
async function loadComments() {
  try {
    const response = await axios.get(
      "https://campus-forum-production-2e9a.up.railway.app/api/admin/comments",
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    comments.value = response.data.data
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

    commentsMessage.value =
      error.response?.data?.message ||
      "获取评论列表失败"
  } finally {
    commentsLoading.value = false
  }
}




//加载板块
async function loadCategories() {
  try {
    const response = await axios.get(
      "https://campus-forum-production-2e9a.up.railway.app/api/admin/categories",
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    categories.value = response.data.data
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

    categoriesMessage.value =
      error.response?.data?.message ||
      "获取板块列表失败"
  } finally {
    categoriesLoading.value = false
  }
}







//  封禁/恢复用户
async function toggleUserStatus(user) {
  const newStatus =
    user.status === "active" ? "banned" : "active"        //当前是 active，就准备改成 banned。当前是 banned，就准备改回 active。

  try {
    const response = await axios.patch(
      `https://campus-forum-production-2e9a.up.railway.app/api/admin/users/${user.id}/status`,
      {
        status: newStatus
      },
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    user.status = response.data.data.status
    alert(response.data.message)
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
      error.response?.data?.message ||
      "修改用户状态失败"
    )
  }
}




//更改帖子状态
async function updatePostStatus(post, newStatus) {
  try {
    const response = await axios.patch(
      `https://campus-forum-production-2e9a.up.railway.app/api/admin/posts/${post.id}/status`,
      {
        status: newStatus
      },
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    post.status = response.data.data.status
    alert(response.data.message)
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
      error.response?.data?.message ||
      "修改帖子状态失败"
    )
  }
}



//隐藏/恢复评论函数
async function updateCommentStatus(comment, newStatus) {
  try {
    const response = await axios.patch(
      `https://campus-forum-production-2e9a.up.railway.app/api/admin/comments/${comment.id}/status`,
      {
        status: newStatus
      },
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    comment.status = response.data.data.status
    alert(response.data.message)
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
      error.response?.data?.message ||
      "修改评论状态失败"
    )
  }
}




//停用/恢复板块函数
async function toggleCategoryStatus(category) {
  const newStatus =
    category.status === "active"
      ? "inactive"
      : "active"

  try {
    const response = await axios.patch(
      `https://campus-forum-production-2e9a.up.railway.app/api/admin/categories/${category.id}/status`,
      {
        status: newStatus
      },
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    category.status = response.data.data.status
    alert(response.data.message)
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
      error.response?.data?.message ||
      "修改板块状态失败"
    )
  }
}





//创建板块
async function createCategory() {
  try {
    const response = await axios.post(
      "https://campus-forum-production-2e9a.up.railway.app/api/admin/categories",
      categoryForm,
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    alert(response.data.message)

    categoryForm.name = ""
    categoryForm.description = ""
    categoryForm.sort_order = 0

    await loadCategories()
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
      error.response?.data?.message ||
      "创建板块失败"
    )
  }
}

onMounted(loadUsers)
onMounted(loadPosts)
onMounted(loadComments)
onMounted(loadCategories)
</script>

<template>
  <main class="admin-page">
    <h1>管理员后台</h1>

    <p v-if="loading">
      正在加载用户列表……
    </p>

    <p v-else-if="message">
      {{ message }}
    </p>

    <section v-else class="user-management">
      <h2>用户管理</h2>

      <p v-if="users.length === 0">
        暂无用户
      </p>

      <table v-else class="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>状态</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="user in users"
            :key="user.id"
          >
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>

            <td>
              {{ user.role === "admin" ? "管理员" : "普通用户" }}
            </td>

            <td>
              {{ user.status === "active" ? "正常" : "已封禁" }}
            </td>

            <td>
              {{ new Date(user.created_at).toLocaleString() }}    <!--注册时间-->
            </td>
            <td>
              <button
                  type="button"
                  @click="toggleUserStatus(user)"
              >
                {{ user.status === "active" ? "封禁" : "恢复" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
    <section class="post-management">
  <h2>帖子管理</h2>

  <p v-if="postsLoading">
    正在加载帖子列表……
  </p>

  <p v-else-if="postsMessage">
    {{ postsMessage }}
  </p>

  <p v-else-if="posts.length === 0">
    暂无帖子
  </p>

      <table v-else class="post-table">
        <thead>
        <tr>
          <th>ID</th>
          <th>标题</th>
          <th>作者</th>
          <th>板块</th>
          <th>状态</th>
          <th>发布时间</th>
          <th>操作</th>
        </tr>
        </thead>

        <tbody>
        <tr
            v-for="post in posts"
            :key="post.id"
        >
          <td>{{ post.id }}</td>
          <td>{{ post.title }}</td>
          <td>{{ post.author.username }}</td>
          <td>{{ post.category.name }}</td>

          <td>
          <span v-if="post.status === 'published'">
            正常
          </span>

            <span v-else-if="post.status === 'hidden'">
            已隐藏
          </span>

            <span v-else>
            已删除
          </span>
          </td>

          <td>
            {{ new Date(post.created_at).toLocaleString() }}
          </td>

          <td>
            <button
                v-if="post.status === 'published'"
                type="button"
                @click="updatePostStatus(post, 'hidden')"
            >
              隐藏
            </button>

            <button
                v-else-if="post.status === 'hidden'"
                type="button"
                @click="updatePostStatus(post, 'published')"
            >
              恢复
            </button>

            <span v-else>
    不可操作
  </span>
          </td>
        </tr>
        </tbody>
      </table>
    </section>
    <section class="comment-management">
  <h2>评论管理</h2>

  <p v-if="commentsLoading">
    正在加载评论列表……
  </p>

  <p v-else-if="commentsMessage">
    {{ commentsMessage }}
  </p>

  <p v-else-if="comments.length === 0">
    暂无评论
  </p>

  <table v-else class="comment-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>评论内容</th>
        <th>作者</th>
        <th>所属帖子</th>
        <th>状态</th>
        <th>发表时间</th>
        <th>操作</th>
      </tr>
    </thead>

    <tbody>
    <tr
        v-for="comment in comments"
        :key="comment.id"
    >
      <td>{{ comment.id }}</td>
      <td>{{ comment.content }}</td>
      <td>{{ comment.author.username }}</td>
      <td>{{ comment.post.title }}</td>

      <td>
          <span v-if="comment.status === 'published'">
            正常
          </span>

        <span v-else-if="comment.status === 'hidden'">
            已隐藏
          </span>

        <span v-else>
            已删除
          </span>
      </td>

      <td>
        {{ new Date(comment.created_at).toLocaleString() }}
      </td>

      <td>
        <button
            v-if="comment.status === 'published'"
            type="button"
            @click="updateCommentStatus(comment, 'hidden')"
        >
          隐藏
        </button>

        <button
            v-else-if="comment.status === 'hidden'"
            type="button"
            @click="updateCommentStatus(comment, 'published')"
        >
          恢复
        </button>

        <span v-else>
            不可操作
          </span>
      </td>
    </tr>
    </tbody>
  </table>
    </section>
    <section class="category-management">
  <h2>板块管理</h2>
      <form
  class="category-form"
  @submit.prevent="createCategory"
>
  <input
    v-model.trim="categoryForm.name"
    type="text"
    placeholder="板块名称"
    required
  >

  <input
    v-model.trim="categoryForm.description"
    type="text"
    placeholder="板块说明"
  >

  <input
    v-model.number="categoryForm.sort_order"
    type="number"
    placeholder="排序"
  >

  <button type="submit">
    创建板块
  </button>
</form>

  <p v-if="categoriesLoading">
    正在加载板块列表……
  </p>

  <p v-else-if="categoriesMessage">
    {{ categoriesMessage }}
  </p>

      <p v-else-if="categories.length === 0">
        暂无板块
      </p>

      <table v-else class="category-table">
        <thead>
        <tr>
          <th>ID</th>
          <th>板块名称</th>
          <th>说明</th>
          <th>排序</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
        </thead>

        <tbody>
        <tr
            v-for="category in categories"
            :key="category.id"
        >
          <td>{{ category.id }}</td>
          <td>{{ category.name }}</td>
          <td>{{ category.description || "暂无说明" }}</td>
          <td>{{ category.sort_order }}</td>

          <td>
            {{ category.status === "active" ? "正常" : "已停用" }}
          </td>

          <td>
            <button
                type="button"
                @click="toggleCategoryStatus(category)"
            >
              {{ category.status === "active" ? "停用" : "恢复" }}
            </button>
          </td>
        </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>

<style scoped>
.admin-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 20px;
}

.admin-page h1 {
  margin-bottom: 24px;
}

.user-management,
.post-management,
.comment-management,
.category-management {
  margin-top: 24px;
  padding: 20px;
  overflow-x: auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgb(0 0 0 / 8%);
}

.user-management h2,
.post-management h2,
.comment-management h2,
.category-management h2 {
  margin-top: 0;
  margin-bottom: 16px;
}

.user-table,
.post-table,
.comment-table,
.category-table {
  width: 100%;
  min-width: 800px;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  vertical-align: middle;
}

th {
  background: #f3f4f6;
  font-weight: 600;
}

tbody tr:hover {
  background: #f9fafb;
}

td {
  word-break: break-word;
}

button {
  padding: 6px 14px;
  color: white;
  background: #2563eb;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

button:hover {
  background: #1d4ed8;
}

@media (max-width: 768px) {
  .admin-page {
    padding: 20px 12px;
  }
}

.category-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.category-form input {
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}
</style>