import { createRouter, createWebHistory } from "vue-router"
import HomeView from "../views/HomeView.vue"
import LoginView from "../views/LoginView.vue"
import PostDetailView from "../views/PostDetailView.vue"
import RegisterView from "../views/RegisterView.vue"
import CreatePostView from "../views/CreatePostView.vue"
import ProfileView from "../views/ProfileView.vue"
import EditPostView from "../views/EditPostView.vue"
import { role, token } from "../stores/auth"
import AdminView from "../views/AdminView.vue"

const router = createRouter({
    history: createWebHistory(),

    routes: [
        {
            path: "/",
            component: HomeView
        },
        {
            path: "/login",
            component: LoginView
        },
        {
            path: "/posts/create",
            name: "post-create",
            component: CreatePostView,
            meta: { requiresAuth: true }         //meta 是附加说明，不会自动执行功能,表示我们给这条路由做了一个标记：“需要登录
        },
        {
            path: "/posts/:id",
            component: PostDetailView
        },
        {
            path: "/register",
            name: "register",
            component: RegisterView       //访问 /register 时，让 <RouterView /> 显示 RegisterView.vue
        },
        {
            path: "/profile",
            name: "profile",
            component: ProfileView,
            meta: { requiresAuth: true }
        },
        {
            path: "/posts/:id/edit",
            name: "post-edit",
            component: EditPostView,
            meta: {requiresAuth: true}
        },
        {
            path: "/admin",
            name: "admin",
            component: AdminView,
            meta: {
                requiresAuth: true,
                requiresAdmin: true
            }
        }

    ]
})

//to表示“准备前往的目标路由”。
//导航守卫
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !token.value) {
    return "/login"
  }

  if (to.meta.requiresAdmin && role.value !== "admin") {
    return "/"
  }
})

export default router