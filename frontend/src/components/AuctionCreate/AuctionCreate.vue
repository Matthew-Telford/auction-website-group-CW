<script setup lang="ts">
    import { getCSRFToken } from "@/utils/csrf";
    import { ref } from "vue";
    import { Button } from "@/components/ui/button";
    import { Input } from "@/components/ui/input";
    import { Label } from "@/components/ui/label";
    //import { Textarea } from "@/components/ui/textarea"; // Ensure you have this or use standard <textarea>
    import {
      Dialog,
      DialogContent,
      DialogDescription,
      DialogFooter,
      DialogHeader,
      DialogTitle,
      DialogTrigger,
    } from "@/components/ui/dialog";
    
    const emit = defineEmits(["item-created"]);
    const isOpen = ref(false);
    const isLoading = ref(false);
    
    const formData = ref({
      title: "",
      description: "",
      minimum_bid: "",
      auction_end_date: "",
    });
    const selectedFile = ref<File | null>(null);
    
    const onFileChange = (e: Event) => {
      const target = e.target as HTMLInputElement;
      if (target.files && target.files[0]) {
        selectedFile.value = target.files[0];
      }
    };
    
    
    const onSubmit = async () => {
      /*
      if (!selectedFile.value) {
        alert("Please upload a picture!");
        return;
      }
      */
      isLoading.value = true;
      
      // 1. Build FormData
      const payload = new FormData();
      payload.append("title", formData.value.title);
      payload.append("description", formData.value.description);
      payload.append("minimum_bid", formData.value.minimum_bid);
      payload.append("auction_end_date", formData.value.auction_end_date);
      console.log("Selected file:", selectedFile.value);
      if (selectedFile.value) {
        payload.append("item_image", selectedFile.value);
      }
    
      try {
        // 2. Send to Backend
        const csrftoken = getCSRFToken();
        const res =await fetch("http://localhost:8000/items/create/", {
        method: "POST",
        credentials: "include",
        body: payload,
        });
    
        const data = await res.json();
        
        if (res.ok) {
          alert("Auction started successfully!");
          isOpen.value = false; // Close modal
          emit("item-created"); // Tell parent page to refresh
          
          // Reset Form
          formData.value = { title: "", description: "", minimum_bid: "", auction_end_date: "" };
          selectedFile.value = null;
        } else {
          alert("Error: " + data.error);
        }
      } catch (err) {
        console.error(err);
        alert("Upload failed.");
      } finally {
        isLoading.value = false;
      }
    };
    </script>
    
    <template>
      <Dialog v-model:open="isOpen">
        <DialogTrigger as-child>
          <Button class="bg-green-600 hover:bg-green-700 text-white">
            + List New Item
          </Button>
        </DialogTrigger>
        <DialogContent class="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create Auction Listing</DialogTitle>
            <DialogDescription>
              Fill in the details for the item you want to sell.
            </DialogDescription>
          </DialogHeader>
    
          <div class="grid gap-4 py-4">
            <div class="grid gap-2">
              <Label htmlFor="title">Item Title</Label>
              <Input id="title" v-model="formData.title" placeholder="e.g. Vintage Camera" />
            </div>
    
            <div class="grid gap-2">
              <Label htmlFor="desc">Description</Label>
              <textarea 
                id="desc" 
                v-model="formData.description" 
                class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Describe the condition, age, etc."
              ></textarea>
            </div>
    
            <div class="grid grid-cols-2 gap-4">
              <div class="grid gap-2">
                <Label htmlFor="price">Starting Price ($)</Label>
                <Input id="price" type="number" step="0.01" v-model="formData.minimum_bid" />
              </div>
              <div class="grid gap-2">
                <Label htmlFor="date">End Date/Time</Label>
                <Input id="date" type="date" v-model="formData.auction_end_date" />
              </div>
            </div>
    
            <div class="grid gap-2">
              <Label htmlFor="picture">Item Picture</Label>
              <Input id="picture" type="file" @change="onFileChange" />
            </div>
          </div>
    
          <DialogFooter>
            <Button @click="onSubmit" :disabled="isLoading">
              {{ isLoading ? 'Listing...' : 'Start Auction' }}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </template>