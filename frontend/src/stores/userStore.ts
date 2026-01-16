import { defineStore } from "pinia";
import { ref, computed } from "vue";

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  profile_picture?: string;
}

export const useUserStore = defineStore("user", () => {
  const user = ref<User | null>(null);

  const isLoggedIn = computed(() => user.value !== null);

  const setUser = (userData: User) => {
    user.value = userData;
  };

  const clearUser = () => {
    user.value = null;
  };

  const fetchUserProfile = async () => {
    try {
      const response = await fetch("http://localhost:8000/profile/", {
        method: "GET",
        credentials: "include",
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        return true;
      } else {
        clearUser();
        return false;
      }
    } catch (err) {
      console.error("Error fetching user profile:", err);
      clearUser();
      return false;
    }
  };

  return {
    user,
    isLoggedIn,
    setUser,
    clearUser,
    fetchUserProfile,
  };
});
