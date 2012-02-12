-- phpMyAdmin SQL Dump
-- version 3.4.9
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2012 年 02 月 12 日 23:27
-- 服务器版本: 5.5.20
-- PHP 版本: 5.3.10

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- 数据库: `onlinejudge`
--

-- --------------------------------------------------------

--
-- 表的结构 `auth`
--

CREATE TABLE IF NOT EXISTS `auth` (
  `uid` int(11) NOT NULL,
  `secret` varchar(100) NOT NULL,
  `create` datetime NOT NULL,
  KEY `uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `member`
--

CREATE TABLE IF NOT EXISTS `member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(200) NOT NULL,
  `username_lower` varchar(200) NOT NULL,
  `password` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `create` datetime NOT NULL,
  `website` varchar(200) DEFAULT NULL,
  `tagline` text,
  `bio` mediumtext,
  `admin` tinyint(1) NOT NULL DEFAULT '0',
  `lang` int(11) NOT NULL DEFAULT '1' COMMENT '1 - pas 2 - c 3 - c++',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `problem`
--

CREATE TABLE IF NOT EXISTS `problem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text NOT NULL,
  `shortname` text NOT NULL,
  `content` mediumtext NOT NULL,
  `content_html` mediumtext NOT NULL,
  `inputfmt` text NOT NULL,
  `outputfmt` text NOT NULL,
  `samplein` text NOT NULL,
  `sampleout` text NOT NULL,
  `create` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `reset_mail`
--

CREATE TABLE IF NOT EXISTS `reset_mail` (
  `uid` int(11) NOT NULL,
  `secret` varchar(100) NOT NULL,
  `create` datetime NOT NULL,
  KEY `uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 限制导出的表
--

--
-- 限制表 `auth`
--
ALTER TABLE `auth`
  ADD CONSTRAINT `auth_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `member` (`id`);

--
-- 限制表 `reset_mail`
--
ALTER TABLE `reset_mail`
  ADD CONSTRAINT `reset_mail_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `member` (`id`);
