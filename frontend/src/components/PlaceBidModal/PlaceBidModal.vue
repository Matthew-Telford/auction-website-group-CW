<script setup lang="ts">
import { ref } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'

interface Bid {
  id: number
  amount: number
  bidder: string
  timestamp: string
}

interface Props {
  itemTitle?: string
  currentHighestBid?: number
  auctionEndTime?: string
  liveBids?: Bid[]
}

const props = withDefaults(defineProps<Props>(), {
  itemTitle: 'Auction Item',
  currentHighestBid: 0,
  auctionEndTime: '',
  liveBids: () => [],
})

const userBid = ref<number | null>(null)
const isOpen = ref(false)

defineExpose({
  isOpen,
})
</script>

<template>
  <Dialog v-model:open="isOpen">
    <DialogTrigger as-child>
      <slot />
    </DialogTrigger>
    <DialogContent class="sm:max-w-[600px]">
      <DialogHeader>
        <DialogTitle>{{ itemTitle }}</DialogTitle>
        <DialogDescription>Place your bid for this item</DialogDescription>
      </DialogHeader>

      <div class="space-y-6 py-4">
        <!-- Countdown Timer -->
        <div class="text-center">
          <Label class="text-sm text-muted-foreground">Auction Ends In</Label>
          <div class="text-3xl font-bold text-primary mt-2">
            00:00:00:00
          </div>
          <p class="text-xs text-muted-foreground mt-1">Days : Hours : Minutes : Seconds</p>
        </div>

        <Separator />

        <!-- Bidding Section -->
        <div class="grid grid-cols-2 gap-6">
          <!-- Current Highest Bid -->
          <div class="space-y-2">
            <Label class="text-sm text-muted-foreground">Current Highest Bid</Label>
            <div class="flex flex-col items-center justify-center h-24 bg-muted rounded-lg">
              <span class="text-4xl font-bold">${{ currentHighestBid.toLocaleString() }}</span>
            </div>
          </div>

          <!-- Your Bid Input -->
          <div class="space-y-2">
            <Label for="bid-amount">Your Bid</Label>
            <div class="flex flex-col gap-2">
              <div class="relative flex items-center h-24 bg-muted rounded-lg px-4">
                <span class="text-3xl font-semibold text-muted-foreground mr-2">$</span>
                <Input
                  id="bid-amount"
                  v-model="userBid"
                  type="number"
                  placeholder="Enter amount"
                  class="border-0 bg-transparent text-3xl font-semibold h-full focus-visible:ring-0 focus-visible:ring-offset-0 p-0"
                  :min="currentHighestBid + 1"
                />
              </div>
              <p class="text-xs text-muted-foreground">
                Minimum bid: ${{ (currentHighestBid + 1).toLocaleString() }}
              </p>
            </div>
          </div>
        </div>

        <Separator />

        <!-- Live Bids Section -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <Label class="text-sm font-semibold">Live Bids</Label>
            <Badge variant="secondary">{{ liveBids.length }} bids</Badge>
          </div>

          <ScrollArea class="h-[200px] w-full rounded-md border p-4">
            <div v-if="liveBids.length === 0" class="flex items-center justify-center h-full text-muted-foreground text-sm">
              No bids yet. Be the first to bid!
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="bid in liveBids"
                :key="bid.id"
                class="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
              >
                <div class="flex items-center gap-3">
                  <Badge variant="outline" class="font-mono">
                    ${{ bid.amount.toLocaleString() }}
                  </Badge>
                  <span class="text-sm font-medium">{{ bid.bidder }}</span>
                </div>
                <span class="text-xs text-muted-foreground">{{ bid.timestamp }}</span>
              </div>
            </div>
          </ScrollArea>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="isOpen = false">Cancel</Button>
        <Button type="submit">Place Bid</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
