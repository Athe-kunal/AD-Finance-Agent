<template>
  <a-layout>
    <a-layout-sider class="sider"> </a-layout-sider>
    <a-layout-content class="content">
      <a-select
        ref="select"
        v-model:value="store.model"
        placeholder="Please select a model"
        class="model-selection"
        size="large"
      >
        <a-select-option value="MOD_HYDE">Modified HYDE</a-select-option>
        <a-select-option value="HYDE">HYDE</a-select-option>
        <a-select-option value="FROZEN">Frozen</a-select-option>
        <a-select-option value="SQL">SQL</a-select-option>
      </a-select>
      <chat-box></chat-box>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { useModelStore } from '@/stores/counter'
import ChatBox from '@/components/ChatBox.vue'

const store = useModelStore()
</script>

<style lang="scss" scoped>
.chat-screen {
  width: 100vw;
  max-width: 100vw;
  height: 100vh;
  max-height: 100vh;

  overflow: hidden;
}

.sider {
  min-width: 300px !important;
  // color: white;
  background-color: white;
}

.content {
  width: calc(100vw - 300px);
  height: 100vh;

  box-sizing: border-box;
  padding: 20px;

  display: flex;
  flex-direction: column;
  align-items: center;
}

.model-selection {
  width: 700px;
}
</style>
