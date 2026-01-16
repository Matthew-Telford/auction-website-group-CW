<script setup lang="ts">
import { ref } from "vue";
import PlaceBidModal from "@/components/PlaceBidModal/PlaceBidModal.vue";
import { Button } from "@/components/ui/button";

const mockLiveBids = ref([
  {
    id: 1,
    amount: 5500,
    bidder: "john_doe",
    timestamp: "2 minutes ago",
  },
  {
    id: 2,
    amount: 5200,
    bidder: "jane_smith",
    timestamp: "5 minutes ago",
  },
  {
    id: 3,
    amount: 5000,
    bidder: "mike_wilson",
    timestamp: "8 minutes ago",
  },
  {
    id: 4,
    amount: 4800,
    bidder: "sarah_jones",
    timestamp: "12 minutes ago",
  },
  {
    id: 5,
    amount: 4500,
    bidder: "david_brown",
    timestamp: "15 minutes ago",
  },
  {
    id: 6,
    amount: 4200,
    bidder: "emily_davis",
    timestamp: "20 minutes ago",
  },
  {
    id: 7,
    amount: 4000,
    bidder: "chris_miller",
    timestamp: "25 minutes ago",
  },
]);
</script>

<template>
  <div class="container mx-auto p-8">
    <div class="max-w-2xl mx-auto">
      <h1 class="text-3xl font-bold mb-6">Vintage Rolex Submariner</h1>
      <p class="text-muted-foreground mb-8">
        Click the button below to view the bid modal with mock data
      </p>

      <PlaceBidModal
        item-title="Vintage Rolex Submariner"
        :current-highest-bid="5500"
        auction-end-time="2026-01-17T15:30:00"
        :live-bids="mockLiveBids"
      >
        <Button size="lg" class="w-full">Place Bid</Button>
      </PlaceBidModal>
    </div>
  </div>
</template>
