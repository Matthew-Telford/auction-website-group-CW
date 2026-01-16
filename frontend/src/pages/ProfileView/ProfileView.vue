<script setup lang="ts">
  import { ref, onMounted } from "vue";
  import ProfileEditModal from "@/components/ProfileModal/ProfileModal.vue";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { useRouter } from "vue-router";
  import { Button } from "@/components/ui/button";
import { getCSRFToken } from "@/utils/csrf";
import { profile } from "node:console";
  
  // Define the profile data interface
  interface ProfileData {
    profile_image: string | null;
    first_name: string;
    last_name: string;
    email: string;
    date_of_birth: string;
    [key: string]: any; // Allow other properties
  }
  
  const profileData = ref<ProfileData | null>(null);
  const isLoading = ref(true);
  
  // 1. Fetch Data
  const fetchProfile = async () => {
  try {
    const res = await fetch("http://localhost:8000/profile/", {
        method: "GET",
        credentials: "include",
    });
    console.log("results from image upload: ", res);
    
    // If the server returns a 404 or 403, we know it's not JSON
    if (!res.ok) {
      console.error("Server responded with error:", res.status);
      return;
    }

    const data = await res.json();
    profileData.value = data;
    
  } catch (err) {
    console.error("Could not parse JSON. Are you logged in?", err);
  } finally {
    isLoading.value = false;
  }
};
  
  // 2. Save Data (JSON Mode)
  const handleSave = async (payload: any) => {
    console.log("payload: ", payload);
    const csrfToken = getCSRFToken();
    try {
      
      await fetch("http://localhost:8000/profile/update/", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken ?? "",
        },
        credentials: "include",
        body: JSON.stringify({
            first_name: payload.first_name ?? "John",
            last_name: payload.last_name ?? "Doe",
            date_of_birth: payload.date_of_birth ?? profileData.value?.date_of_birth,
        }),
    });
      const formData = new FormData();
        // Optionally, log a warning or handle cases where profile_picture is not a valid file
        formData.append("profile_picture", payload.profile_picture);
      const res=await fetch("http://localhost:8000/profile/picture/upload/", {
          method: "POST",
          credentials: "include",
          headers: {
            "X-CSRFToken": csrfToken || "",
          },
          body: formData,
      });
      
      if (res.ok) {
        await fetchProfile();
      } else {
        alert("Something went wrong");
      }
    } catch (err) {
      console.error(err);
    }
  };
  
  onMounted(fetchProfile);
  </script>
  
  <template>
    <div class="container bg-transparent mx-auto p-10 max-w-2xl">
      <Card v-if="profileData">
        <CardHeader class="flex flex-row items-center justify-between">
          <CardTitle>My Profile</CardTitle>
          <ProfileEditModal :initial-data="profileData" @save="handleSave" />
          <Button as-child class="bg-blue-600 hover:bg-blue-700 text-white">
              <router-link to="/itemUpload">
                Manage Listings
              </router-link>
            </Button>
        </CardHeader>
        
        <CardContent class="space-y-6">
          <div class="flex items-center gap-6">
            <img 
              class="rounded-full overflow-hidden max-w-200 max-h-200 rounded-full h-20 w-20 object-cover"
              size="sm"
              v-if="profileData.profile_picture"
              :src="profileData.profile_picture" 
              @error="(e) => console.error('Image failed to load:', e)"
              :key="profileData.profile_picture"
            />
            <div>
              <h2 class="text-2xl font-bold">
                {{ profileData.first_name }} {{ profileData.last_name }}
              </h2>
              <p class="text-gray-500">{{ profileData.email }}</p>
              <p class="text-sm text-gray-400 mt-1">Born: {{ profileData.date_of_birth }}</p>
            </div>
          </div>
        </CardContent>
      </Card>
  
      <div v-else class="text-center mt-10">Loading...</div>
    </div>
  </template>