<script setup lang="ts">
import { PropType } from 'vue'
import { Descriptions, DescriptionsSchema } from '@/components/Descriptions'
import { DepartmentItem } from '@/api/department/types'

defineProps({
  currentRow: {
    type: Object as PropType<Nullable<DepartmentItem>>,
    default: () => null
  },
  detailSchema: {
    type: Array as PropType<DescriptionsSchema[]>,
    default: () => []
  }
})
</script>

<template>
  <Descriptions :schema="detailSchema" :data="currentRow || {}" />
</template>
