<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <a-config-provider
    :theme="{
      token: {
        colorPrimary: '#2ecc71'
      }
    }"
  >
    <header></header>

    <RouterView />
  </a-config-provider>
</template>
