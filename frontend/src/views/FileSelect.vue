<template>
  <div class="page file-select">
    <h2>文件选择</h2>

    <a-table
      :columns="columns"
      :data-source="files"
      row-key="name"
      row-selection="{ type: 'checkbox', selectedRowKeys: selectedKeys, onChange: onSelect }"
      bordered
    />

    <div style="margin-top: 20px; text-align: right">
      <a-button
        type="primary"
        :disabled="selectedKeys.length === 0"
        @click="startAnalysis"
      >
        开始分析
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { listFiles, startJob } from '@/api'
import { message } from "ant-design-vue";

const router = useRouter();
const files = ref<any[]>([]);
const selectedKeys = ref<string[]>([]);

const columns = [
  { title: "文件名", dataIndex: "name" },
  { title: "大小", dataIndex: "size" },
  { title: "日期", dataIndex: "date" },
];

onMounted(async () => {
  const res = await api.listFiles();
  files.value = res.data ?? [];
});

function onSelect(keys: string[]) {
  selectedKeys.value = keys;
}

async function startAnalysis() {
  const res = await api.startJob({ files: selectedKeys.value });
  message.success("任务已启动");
  router.push("/progress");
}
</script>

<style scoped>
.page {
  padding: 20px;
}
</style>
