// Example of how to use Vue Router

import { createRouter, createWebHistory } from "vue-router";

// 1. Define route components.
// These can be imported from other files
import MainPage from "../pages/MainPage.vue";
import OtherPage from "../pages/OtherPage.vue";
import LoginPage from "@/pages/LoginPage/LoginPage.vue";
import SignupPage from "@/pages/SignupPage/SignupPage.vue";
import ProfileView from "@/pages/ProfileView/ProfileView.vue";
import ItemDetailsPage from "@/pages/ItemDetailsPage/ItemDetailsPage.vue";
import AuctionUploadPage from "@/pages/AuctionUploadPage/AuctionUploadPage.vue";

let base =
  import.meta.env.MODE == "development" ? import.meta.env.BASE_URL : "";

// 2. Define some routes
// Each route should map to a component.
// We'll talk about nested routes later.
const router = createRouter({
  history: createWebHistory(base),
  routes: [
    { path: "/", name: "Main Page", component: MainPage },
    { path: "/other/", name: "Other Page", component: OtherPage },
    { path: "/login", name: "LoginPage", component: LoginPage },
    { path: "/signup", name: "SignupPage", component: SignupPage },
    { path: "/profile",name: "Profile Page", component:ProfileView},
    {
      path: "/itemDetailsPage/:id",
      name: "ItemDetailsPage",
      component: ItemDetailsPage,
    },
    { path: "/itemUpload",name: "AuctionUploadPage", component:AuctionUploadPage},
  ],
});

export default router;
