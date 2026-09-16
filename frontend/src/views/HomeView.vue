<script setup>
import {onMounted, ref} from "vue"
import axios from "axios"

const title = "校园论坛"             //const 是JavaScript中声明变量的关键字，表示：这个变量声明以后，不能再被重新赋值。
const posts = ref([])       //ref() 的作用是：创建一个Vue能够监视的响应式数据。
const loading = ref(true)      //true 表示页面刚打开时，帖子正在加载。

const pagination = ref({
  page: 1,
  pages: 1,
  total: 0
})

const categories = ref([])
const keyword = ref("")
const selectedCategoryId = ref("")


//加载板块
async function loadCategories() {
  try {
    const response = await axios.get(
      "http://127.0.0.1:5000/api/categories"
    )

    categories.value = response.data.data
  } catch (error) {
    console.error("获取板块失败", error)
  }
}


//加载帖子
async function loadPosts(page = 1) {
  try {
    loading.value = true

    const response = await axios.get(
        "http://127.0.0.1:5000/api/posts",
        {
          params: {
            page: page,
            per_page: 10,
            keyword: keyword.value || undefined,
            category_id: selectedCategoryId.value || undefined
          }
        }
    )

    posts.value = response.data.data
    pagination.value = response.data.pagination
  } catch (error) {
    console.error("获取帖子失败", error)
  } finally {
    loading.value = false
  }
}

function changePage(newPage) {
  if (
    newPage < 1 ||
    newPage > pagination.value.pages
  ) {
    return
  }

  loadPosts(newPage)
}


//查找帖子
function searchPosts() {
  loadPosts(1)
}

//重置筛选条件
function resetFilters() {
  keyword.value = ""
  selectedCategoryId.value = ""

  loadPosts(1)
}

onMounted(loadPosts)      //onMounted 是Vue的生命周期函数，意思是：当 HomeView.vue 已经加载到页面上时，自动执行 loadPosts()
onMounted(loadCategories)


</script>

<template>
  <main class="home">
    <h1>{{ title }}</h1>
    <p>分享校园生活，交流学习经验</p>
    <!--加入搜索表单-->
    <form
        class="filters"
        @submit.prevent="searchPosts"
    >
      <input
          v-model.trim="keyword"
          type="search"
          placeholder="搜索标题或正文"
      >

      <select v-model="selectedCategoryId">
        <option value="">全部板块</option>

        <option
            v-for="category in categories"
            :key="category.id"
            :value="category.id"
        >
          {{ category.name }}
        </option>
      </select>

      <button type="submit">
        搜索
      </button>

      <button
          type="button"
          @click="resetFilters"
      >
        重置
      </button>
    </form>

    <p v-if="loading">
      正在加载帖子……
    </p>

    <p v-else-if="posts.length === 0">
      暂无帖子
    </p>

    <section v-else class="post-list">
      <article
          v-for="post in posts"
          :key="post.id"
          class="post-card"
      >
        <h2>
          <RouterLink :to="`/posts/${post.id}`">
            {{ post.title }}
          </RouterLink>
        </h2>

        <p>作者：{{ post.author.username }}</p>
        <p>板块：{{ post.category.name }}</p>
      </article>
    </section>
    <nav
        v-if="!loading && pagination.pages > 1"
        class="pagination"
    >
      <button
          type="button"
          :disabled="pagination.page === 1"
          @click="changePage(pagination.page - 1)"
      >
    上一页
  </button>

  <span>
    第 {{ pagination.page }} 页，
    共 {{ pagination.pages }} 页，
    {{ pagination.total }} 篇帖子
  </span>

  <button
    type="button"
    :disabled="pagination.page === pagination.pages"
    @click="changePage(pagination.page + 1)"
  >
    下一页
  </button>
</nav>
  </main>
</template>

<style scoped>
.home {
  padding: 40px;
  text-align: center;
}

.post-list {
  margin-top: 40px;
  text-align: left;
}

.post-card {
  margin-bottom: 16px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
}

.post-card h2 {
  margin-top: 0;
}

.post-card a {
  color: #303133;
  text-decoration: none;
}

/*:hover表示鼠标放在链接上时，标题变成蓝色。*/
.post-card a:hover {
  color: #409eff;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.pagination button {
  padding: 8px 14px;
  color: white;
  background: #409eff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.pagination button:disabled {
  cursor: not-allowed;
  background: #a8abb2;
}

.filters {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 24px;
}

.filters input,
.filters select,
.filters button {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

.filters button {
  color: white;
  cursor: pointer;
  background: #409eff;
  border: none;
}
</style>