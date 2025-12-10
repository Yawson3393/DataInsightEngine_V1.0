<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header
      style="background: #001529; color: white; display: flex; align-items: center;">
      <h2 style="color: white; margin: 0">电池堆大数据分析平台</h2>
    </a-layout-header>

    <a-layout-content style="padding: 20px;">
      <router-view />
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts"></script>

<style>
body {
  margin: 0;
  background: #f0f2f5;
}
</style>
