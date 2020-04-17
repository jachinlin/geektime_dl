<template>
  <el-card shadow="hover" class="post-card">
    <el-row @click="go(post.path)">
      <el-col :lg="10" :md="12" :sm="12" v-if="post.image" class="post-cover">
        <img :src="$withBase(post.image)" :alt="post.title" >
      </el-col>
      <el-col :lg="14" :md="12" :sm="12" class="post-content">
        <div>
          <h2 class="post-title">
            <a :href="post.path" target="_blank">{{ post.title }}</a>
          </h2>
        </div>
        <div class="post-summary" v-if="post.summary">
          <p>
            {{ post.summary }}
            <a :href="post.path" target="_blank" class="post-read-more">
              {{ post.readMoreText || 'Read more'}}
            </a>
          </p>
        </div>
      </el-col>
    </el-row>
    <div class="post-footer">
      <div class="post-footer-item">
        <CalendarIcon class="post-footer-item-icon"/>
        {{ new Date(post.date.trim()).toDateString() }}
      </div>
      <div class="post-footer-item" v-if="post.readingTime">
        <ClockIcon class="post-footer-item-icon"/>
        {{ post.readingTime }}
      </div>
      <div class="post-footer-item" v-if="post.location">
        <NavigationIcon class="post-footer-item-icon"/>
        {{ post.location }}
      </div>
    </div>
  </el-card>
</template>

<script>
import { NavigationIcon, ClockIcon, CalendarIcon } from "vue-feather-icons";

export default {
  name: 'post-card',
  props: {
    post: {
      type: Object,
      required: true
    }
  },
  components: { NavigationIcon, ClockIcon, CalendarIcon },
  methods: {
    go (path) {
      this.$router.push(path)
    }
  }
}
</script>

<style>
  .post-card {
  }
  .post-cover {
    padding: 16px;
  }
  .post-cover img {
    border-radius: 16px;
    width: 100%;
  }
  .post-content {
    padding: 0 20px;
  }
  .post-title {
    margin-bottom: 10px;
  }
  .post-title a {
    color: #6c5b7b;
  }
  .post-summary {
    margin: 10px 0;
    color: #6c757d;
    word-wrap: break-word;
  }
  .post-read-more {
    color: #6c5b7b;
  }
  .post-footer {
    font-size: 13px;
    text-align: left;
    border-top: 1px solid #dee2e6;
    border-color: #f8f9fa;
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
    padding: 20px;
    color: #6c757d;
  }
  .post-footer-item {
    margin-right: 1rem;

  }
  .post-footer-item-icon {
    vertical-align: middle;
    width: 17px;
  }
</style>

