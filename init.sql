SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `response`;
CREATE TABLE `response` (
  `_created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `_updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `response_id` varchar(64) DEFAULT NULL COMMENT '回答ID',
  `user_resp` text COMMENT '用户回答结果',
  `task_id` int(11) DEFAULT NULL COMMENT '任务ID',
  `object_url` text COMMENT '图片路径',
  `cache_id` varchar(64) DEFAULT NULL COMMENT '回答ID',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `ix_response_response_id` (`response_id`),
  KEY `ix_response_task_id` (`task_id`),
  CONSTRAINT `response_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for task
-- ----------------------------
DROP TABLE IF EXISTS `task`;
CREATE TABLE `task` (
  `_created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `_updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` int(11) DEFAULT NULL COMMENT '任务ID',
  `object_url` text COMMENT '图片路径',
  PRIMARY KEY (`id`),
  KEY `ix_task_task_id` (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6304 DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
