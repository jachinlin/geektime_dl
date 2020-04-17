<template>
  <div>
    <post-card
      v-for="post in posts"
      :key="post.key"
      :post="post"
      class="post-card"
      shadow="hover"
    />
  </div>
</template>

<script>
import { columnShareData } from '../../geektime_data.js'
export default {
  data: function () {
    return {
      posts: columnShareData,
    }
  },
  created() {
  }
};
</script>

<style>
.post-card {
  margin-bottom: 20px;
}
</style>
