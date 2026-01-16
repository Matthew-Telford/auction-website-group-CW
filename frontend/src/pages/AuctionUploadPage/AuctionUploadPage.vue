<script setup lang="ts">
    import { ref, onMounted } from "vue";
    import CreateItemModal from "@/components/AuctionCreate/AuctionCreate.vue";
    import { Card, CardContent, CardFooter } from "@/components/ui/card";
    import { Badge } from "@/components/ui/badge";
    import { Package } from "lucide-vue-next";

    interface AuctionItem {
    id: number;
    title: string;
    minimum_bid: string;
    auction_end_date: string;
    image: string | null;
    }
    //Fetching users previous items:
    const myItems = ref<AuctionItem[]>([]);
    const isLoading = ref(true);

    const fetchMyItems = async () => {
        try {
            // Calling the new endpoint we just made
            const res = await fetch("http://localhost:8000/users/me/items/", {
                method: "GET",
                credentials: "include",
            });

            if (!res.ok) {
                throw Error(String(res.status))
            }

            const itemResults = await res.json();

            myItems.value = itemResults.items.map((item) => ({
                id: item.id,
                title: item.title,
                minimum_bid: item.minimum_bid,
                auction_end_date: item.auction_end_date,
                image: item.image,
            }))
        } catch (err) {
            console.error("Error fetching user items:", err);
        } finally {
            isLoading.value = false;
        }
    };
    const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
    };
    // This will store the list of items
    const items = ref([]);
    
    const fetchItems = async () => {
      // You can create a Django GET view later to populate this
      // const res = await fetch("/api/auction/list/");
      // items.value = await res.json();
      console.log("Fetching latest items...");
    };
    onMounted(fetchMyItems);
</script>

<template>
  <div class="container mx-auto p-10 max-w-6xl">
    <div class="flex justify-between items-end mb-8 border-b pb-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">My Listings</h1>
        <p class="text-gray-500 mt-1">Manage the items you are selling.</p>
      </div>
      
      <CreateItemModal @item-created="fetchMyItems" />
    </div>

    <div v-if="isLoading" class="text-center py-20 text-gray-400">
      Loading your inventory...
    </div>

    <div v-else-if="myItems.length === 0" 
     class="flex flex-col items-center justify-center py-20 bg-gray-50 rounded-xl border-2 border-dashed text-center">
    
    <div class="mb-4 text-gray-400">
        <Package :size="48" />
    </div>

    <h3 class="text-lg font-medium">No items listed yet</h3>
    <p class="text-gray-500 max-w-sm mx-auto mt-2 px-6">
        You haven't put anything up for auction. Click the button above to start selling!
    </p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card v-for="item in myItems" :key="item.id" class="overflow-hidden hover:shadow-lg transition-shadow">
        <div class="relative h-48 bg-gray-100">
          <img 
            v-if="item.image" 
            :src="item.image" 
            class="w-full h-full object-cover"
            alt="Item Image"
          />
          <div v-else class="flex items-center justify-center h-full text-gray-400">
            No Image
          </div>
          <Badge class="absolute top-2 right-2 bg-black/50 hover:bg-black/70 text-white">
            Active
          </Badge>
        </div>

        <CardContent class="p-4">
          <h3 class="font-bold text-lg truncate">{{ item.title }}</h3>
          <p class="text-green-600 font-semibold mt-1">${{ item.starting_price }}</p>
          <p class="text-xs text-gray-500 mt-2">
            Ends: {{ formatDate(item.end_time) }}
          </p>
        </CardContent>
        
        <CardFooter class="p-4 pt-0 flex gap-2">
             <button class="text-sm font-medium text-blue-600 hover:underline">
                View Details
            </button>
        </CardFooter>
      </Card>
    </div>
  </div>
</template>